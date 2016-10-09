import tornado.ioloop
import tornado.web
from loka import *
from time import time
import datetime

s = solver()

class handler(tornado.web.RequestHandler):
    def get(self):
        x1 = self.get_argument('location1')
        y1 = self.get_argument('location2')
        x2 = self.get_argument('destination1')
        y2 = self.get_argument('destination2')
        hour = self.get_argument('arrival_hour')
        minute = self.get_argument('arrival_minute')
        num = int(self.get_argument('step'))
        end = self.get_argument('name')
        l= datetime.datetime.fromtimestamp(
            int(time())
        ).strftime('%Y-%m-%d %H:%M:%S')
        min = l[-5:-3]
        ho = l[-8:-6]
        t= (int(hour) - int(ho)) * 60 * 60 + (int(minute) - int(min)) * 60
        print(num)
        #ans = s.make_answer(start=(x1, y1), stop=(x2, y2), time=t, ignored=[], num=num, end=end)
        try:
            ans = s.make_answer(start=(x1, y1), stop=(x2, y2), time=t, ignored=[], num=num, end=end)
            self.write(ans)
        except Exception:
            try:
                ans = s.make_answer(start=(x1, y1), stop=(x2, y2), time=t, ignored=[], num=num+1, end=end)
                self.write(ans)
            except Exception:
                self.write({'error' : "LOL"})
        else:
            print('done')


    def post(self, *args, **kwargs):
        pass

routes = [(r'/route', handler)]
app = tornado.web.Application(routes)
app.listen(8000)
tornado.ioloop.IOLoop.current().start()