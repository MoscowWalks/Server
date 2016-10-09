import json
import random
import requests
import re
class solver():

    def __init__(self):
        f = open('file.json')
        data = json.load(f)
        self.moscow_data = []
        for i in range(len(data['data'])):
            if data['data'][i]['data']['general']['region']['id'] == '77':
                self.moscow_data.append(data['data'][i]['data']['general'])

    def get_pattern(self, path, start, stop):
        pattern = 'https://maps.googleapis.com/maps/api/directions/json?'
        start_coors = start
        stop_coors = stop
        pattern += 'origin=' + start_coors[0] + ',' + start_coors[1] + '&'
        pattern += 'language=ru&'
        pattern += 'destination=' + stop_coors[0] + ',' + stop_coors[1] + '&'
        if len(path):
            pattern += 'waypoints=optimize:true'
        for i in path:
            coors = self.get_coors(i)
            pattern += '|' + coors[0] + ',' + coors[1]
        if len(path):
            pattern += '&'
        pattern += 'avoid=highways&mode=walking&key=AIzaSyCBxjefDqnsyoAwKrg95aaDmRoDFMPeySI'
        return pattern

    def check_path(self, path, time, start, stop):
        pattern = self.get_pattern(path, start, stop)
        r = requests.get(pattern)
        a = json.loads(r.content.decode('utf-8'))
        #print(a)
        return time > self.get_duration(a)

    def get_duration(self, data):
        return data['routes'][0]['legs'][0]['duration']['value']

    def get_coors(self, data):
        return data['coords']['yandexCoord']['x'], data['coords']['yandexCoord']['y']


    def cmp(self, x):
        try:
            x_coor = list(map(float, self.get_coors(x)))
            (x_coor[0] - self.med[0]) ** 2 + (x_coor[1] - self.med[1]) ** 2
            return (x_coor[0] - self.med[0]) ** 2 + (x_coor[1] - self.med[1]) ** 2
        except Exception:
            return 1000000000000

    def find_path(self, start, stop, ignored, time):
        self.med = list(map(float, start))
        self.med[0] = (self.med[0]*2 + list(map(float, stop))[0])/3
        self.med[1] = (self.med[1]*2 + list(map(float, stop))[1]) / 3
        self.current = sorted(self.moscow_data, key=self.cmp)[:100]
        random.shuffle(self.current)
        path = []
        count = 0
        for i in self.current:
            if i['id'] in ignored or len(i['name']) < 10 :
                continue
            path.append(i)
            #print(i)
            count += 1
            if not self.check_path(path=path, time=time, start=start, stop=stop):
                path = path[:-1]
                count -= 1
            if count == 4:
                break
        return path

    def get_json(self, start, stop, path):
        pattern = self.get_pattern(path, start, stop)
        #print(pattern)
        r = requests.get(pattern)
        a = json.loads(r.content.decode('utf-8'))
        return a

    def get_way(self, a, num):
        return [a['routes'][0]['legs'][num]["steps"][i]['html_instructions'] for i in range(len(a['routes'][0]['legs'][num]["steps"]))]

    def get_way_dist(self, a, num):
        return[a['routes'][0]['legs'][num]["steps"][i]['distance']['text'] for i in range(len(a['routes'][0]['legs'][num]["steps"]))]

    def get_index(self, a, num):
        return a['routes'][0]['waypoint_order'][num]

    def get_data_oject(self, path, a, num):
        return path[self.get_index(a, num)]

    def del_tags(self, string):
        string=string.replace('<div style="font-size:0.9em">', '\n')
        return re.sub('<[^<]+?>', '', string)

    def get_image(self, path):
        return 'http://esb.mkrf.ru:8081' + path

    def make_answer(self, start, stop, time, ignored, num, end):
        if num == 0:
            print("gen_path")
            self.path = self.find_path(start=start, stop=stop, time=time, ignored=ignored)
        a = self.get_json(start, stop, self.path)
        if num < len(self.path):
            print("not stop")
            nearest = self.get_data_oject(self.path, a, num=num)
            #address = nearest['address']
            #id = nearest['id']

            name = nearest.get('name', '')
            coords = self.get_coors(nearest)

            try:
                img_pttrn = nearest['photo']['url']
            except Exception:
                img_pttrn = 'https://upload.wikimedia.org/wikipedia/commons/3/39/Domestic_Goose.jpg'
        else:
            coords = stop
        images = self.get_google_images(self.get_google_coors(a, num))
        way = self.get_way(a, num)
        distenses = self.get_way_dist(a, num)
        for i in range(len(way)):
            way[i] = self.del_tags(way[i])
        print('here')
        if num >= len(self.path):
            im = 'https://maps.googleapis.com/maps/api/streetview?size=600x300&location='+ str(stop[0]) + ',' + str(stop[1])+'&heading=151.78&pitch=-0.76&key=AIzaSyCBxjefDqnsyoAwKrg95aaDmRoDFMPeySI&'
            return json.dumps(
                {'distances':distenses,'last':True, "address": 'adress', "coordinates": coords, "id": '00', "name": end+'\n'+'Поздравляем, вы прошли маршрут!', "way": way, 'images': images,
                 'image': im}, ensure_ascii=False)

        #print(json.dumps({"address":address, "coordinates": coords, "id":id, "name":name, "way":way, 'images':images}, ensure_ascii=False))
        return json.dumps({'distances':distenses,'last':False,"address":'00', "coordinates": coords, "id":'00', "name":name, "way":way, 'images':images, 'image': self.get_image(img_pttrn)}, ensure_ascii=False)

    def get_google_coors(self, a, num):
        return [(a['routes'][0]['legs'][num]["steps"][i]['end_location']['lat'], a['routes'][0]['legs'][num]["steps"][i]['end_location']['lng']) for i in range(len(a['routes'][0]['legs'][num]["steps"]))]

    def get_google_images(self, coors):
        return ['https://maps.googleapis.com/maps/api/streetview?size=600x300&location='+ str(coors[i][0]) + ',' + str(coors[i][1])+'&heading=151.78&pitch=-0.76&key=AIzaSyCBxjefDqnsyoAwKrg95aaDmRoDFMPeySI&' for i in range(len(coors))]