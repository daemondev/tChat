import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.ioloop
from tornado.escape import json_encode

from tornado import gen

import json
from threading import Thread
from datetime import datetime
import os

global thread
thread = None

### For RethinkDB
import rethinkdb as r
from rethinkdb import RqlRuntimeError, RqlDriverError

r.set_loop_type("tornado")


@gen.coroutine
def create_chat(data):
    data = json.loads(data)
    #print(data)
    print(">>>> ",data['1'])

    data = json.loads(data["1"])
    data['created'] = datetime.now(r.make_timezone('00:00'))
    if data.get('name') and data.get('message'):
        conn = yield r.connect(host="localhost", port=28015, db='chat')
        new_chat = yield r.table("chats").insert([ data ]).run(conn)
        print("success insert in DB")

connections = set()

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    #connections = set()
    def open(self):
        #self.connections.add(self)
        connections.add(self)
        pass

    def on_message(self, message):
        #[con.write_message(json.dumps(message, default=json_util.default)) for con in self.connections]
        print(message)
        create_chat(message)
        [con.write_message(json.dumps(message)) for con in connections]
        #[con.write_message(json.dumps(message)) for con in self.connections]
        #[con.write_message(json_encode(message)) for con in self.connections]
        #self.write_message(u"Your message was: " + message)

    def on_close(self):
        #self.connections.remove(self)
        connections.remove(self)
        pass

def watch_chats():
    print('\n#################################\n###>>> Watching db for new chats!\n#################################\n\n')
    conn = r.connect(host='localhost', port=28015, db='chat')
    feed = r.table("chats").changes().run(conn)
    for chat in feed:
        chat['new_val']['created'] = str(chat['new_val']['created'])
        #socketio.emit('new_chat', chat)

@gen.coroutine
def print_changes():
    conn = yield r.connect(host="localhost", port=28015, db='chat')
    feed = yield r.table("chats").changes().run(conn)
    while (yield feed.fetch_next()):
        change = yield feed.next()
        for c in connections:
            change['new_val']['created'] = str(change['new_val']['created'])
            c.write_message(change)
        print(change)

class IndexPageHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        conn = yield r.connect(host='localhost', port=28015, db='chat')
        chatsr = yield r.table("chats").order_by(index=r.desc('created')).limit(20).run(conn)
        #self.render("index.html", chats=chatsr)

        chats = []
        #"""
        while (yield chatsr.fetch_next()):
            chat = yield chatsr.next()
            chats.append(chat)
            #print("added")
            #print(chats) #"""
        """
        for chat in (yield chatsr.next()):
            # Is guaranteed to have a result since we have already waited on feed.fetch_next
            chats.append(chat)
            print("for loop mode") #"""

        """
        for document in (yield cursor.to_list(length=100)):
            print document #"""

        yield self.render("index.html", chats=chats)
        #yield self.render("index.html", chats=[{'name':'admin', 'message':'test'}])
        print("exit")


class Application(tornado.web.Application):
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        static_folder = os.path.join(current_dir, "static")

        handlers = [
            (r'/', IndexPageHandler),
            (r'/websocket', WebSocketHandler),
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': static_folder})
        ]
        """
        if thread is None:
            thread = Thread(target=watch_chats)
            #thread.setDaemon(True)
            thread.start() #"""



        settings = {
            'template_path': 'templates',
            'debug': True,
            'autorealod': True
        }
        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == '__main__':
    ws_app = Application()
    """
    if thread is None:
        thread = Thread(target=watch_chats)
        #thread.setDaemon(True)
        thread.start() #"""
    server = tornado.httpserver.HTTPServer(ws_app)
    server.listen(8000)
    tornado.ioloop.IOLoop.current().add_callback(print_changes)
    tornado.ioloop.IOLoop.instance().start()
    #tornado.ioloop.IOLoop.current().add_callback(watch_chats)
#https://github.com/rethinkdb/docs/blob/issue-684-async-docs/2-query-language/asynchronous.md#python-and-tornado
#https://github.com/rethinkdb/rethinkdb/issues/2622
#https://github.com/hustlzp/Flask-Boost
#https://stackoverflow.com/questions/11694124/tornado-write-a-jsonp-object
#self.write(self.render_string('index.html', ...)).
#https://impythonist.wordpress.com/2015/08/02/build-a-real-time-data-push-engine-using-python-and-rethinkdb/
#http://www.tornadoweb.org/en/stable/guide/templates.html
#https://impythonist.wordpress.com/2015/08/02/build-a-real-time-data-push-engine-using-python-and-rethinkdb/
