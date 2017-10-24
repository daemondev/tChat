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
import base64

global thread
thread = None

### For RethinkDB
import rethinkdb as r
from rethinkdb import RqlRuntimeError, RqlDriverError

#-------------------------------------------------- BEGIN [DEV MODE] - (19-10-2017 - 11:00:51) {{
#import tornado.wsgi
#-------------------------------------------------- END   [DEV MODE] - (19-10-2017 - 11:00:51) }}

r.set_loop_type("tornado")

@gen.coroutine
def create_chat(data):
    data = json.loads(data)

    action = data['0']
    conn = yield r.connect(host="localhost", port=28015, db='chat')

    if action == "start bot":
        data['action'] = "start"
        data['status'] = 1

        new_action = yield r.table("botActions").insert([ data ]).run(conn)
        print("starting bot")
    elif action == "exit bot":
        data['action'] = "stop"
        data['status'] = 1

        new_action = yield r.table("botActions").insert([ data ]).run(conn)
        print("shutdown bot")
    elif action == "new message":
        data = data["1"]
        data['created'] = datetime.now(r.make_timezone('00:00'))
        if data.get('name') and data.get('message'):
            new_chat = yield r.table("chats").insert([ data ]).run(conn)
        print(">>> end create_chat")

connections = set()

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        connections.add(self)
        pass

    def on_message(self, message):
        #[con.write_message(json.dumps(message, default=json_util.default)) for con in self.connections]
        print(message)
        create_chat(message)

        #[con.write_message(str(message)) for con in connections] #work
        #[con.write_message(json.dumps(message)) for con in self.connections] #Work
        #self.write_message(u"Your message was: " + message)

    def on_close(self):
        connections.remove(self)
        pass

    def check_origin(self, origin):
        #parsed_origin = urllib.parse.urlparse(origin)
        #return parsed_origin.netloc.endswith(".mydomain.com")
        return True

import pyscreenshot
from io import BytesIO

global a
a = 0
@gen.coroutine
def sendDesktop():
    while 1:
        global a
        a = a + 1

        if len(connections) > 0:
            print("\nconexiones WS: %d\n" % len(connections))

            img_buffer = BytesIO()
            pyscreenshot.grab().save(img_buffer, 'PNG', quality=0.1)
            img_buffer.seek(0)
            s = img_buffer.getvalue()

            for c in connections:
                payload = {"event": "show desktop", "data": str(base64.b64encode(s))}
                c.write_message(payload) #"""
        yield gen.sleep(0.5)
        #yield gen.sleep(1.5)
        print(">>> end step: %d" % a)

@gen.coroutine
def watch_chats():
    print('\n#################################\n###>>> Watching db for new chats!\n#################################\n\n')
    conn = yield r.connect(host='localhost', port=28015, db='chat')
    feed = yield r.table("chats").changes().run(conn)
    union = yield r.union(r.table("chats").changes(), r.table("scripts").changes()).run(conn)

    while (yield feed.fetch_next()):
        change = yield feed.next()
        print("\nconexiones WS: %d\n" % len(connections))
        for c in connections:
            change['new_val']['created'] = str(change['new_val']['created'])
            payload = {"event":"new chat","data": change["new_val"]}
            c.write_message(payload)
        print(change)
        print("watching db CHANGES ############")

@gen.coroutine
def print_changes():
    conn = yield r.connect(host="localhost", port=28015, db='chat')
    feed = yield r.table("chats").changes().run(conn)
    while (yield feed.fetch_next()):
        change = yield feed.next()
        for c in connections:
            change['new_val']['created'] = str(change['new_val']['created'])
            payload = {"event":"new chat","data": change["new_val"]}
            #c.write_message(change)
            c.write_message(payload)
        print(change)

class DesktopHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        print("begin desktopShare")
        img_buffer = BytesIO()
        pyscreenshot.grab().save(img_buffer, 'PNG', quality=5)
        img_buffer.seek(0)
        s = img_buffer.getvalue()
        self.set_header('Content-type', 'image/jpg')
        self.set_header('Content-length', len(s))
        self.write(s)
        print("end desktopShare\n")
        #for c in connections:
            #c.write_message(s)

@gen.coroutine
def get(self):
    file_name = 'file.ext'
    buf_size = 4096
    self.set_header('Content-Type', 'application/octet-stream')
    self.set_header('Content-Disposition', 'attachment; filename=' + file_name)
    with open(file_name, 'r') as f:
        while True:
            data = f.read(buf_size)
            if not data:
                break
            self.write(data)
    self.finish()

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
        print("Index Page: Send")


class Application(tornado.web.Application):
    def __init__(self):

        import tornado.autoreload
        tornado.autoreload.start()
        for dir, _, files in os.walk('static'):
            print(files)
            [tornado.autoreload.watch(dir + '/' + f) for f in files if not f.startswith('.')]

        current_dir = os.path.dirname(os.path.abspath(__file__))
        static_folder = os.path.join(current_dir, "static")

        """
        global thread
        if thread is None:
            thread = Thread(target=watch_chats)
            #thread.setDaemon(True)
            thread.start() #"""


        settings = {
            "cookie_secret": "__myKEY:_MDY_BPO_pyCHAT_APP__",
            "login_url": "/login",
            "xsrf_cookies": True,
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
            'template_path': 'templates'
            ,'debug': True,
            'autorealod': True
        }

        handlers = [
            (r'/', IndexPageHandler),
            (r'/screen.png', DesktopHandler),
            (r'/websocket', WebSocketHandler),
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': static_folder})
        ]

        tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == '__main__':
    ws_app = Application()
    #"""
    if thread is None:
        thread = Thread(target=watch_chats)
        thread.setDaemon(True)
        thread.start() #"""

    """
    sockets = tornado.netutil.bind_sockets(8888)
    tornado.process.fork_processes(0)
    server = tornado.httpserver.HTTPServer(ws_app)
    server.add_sockets(sockets)
    tornado.ioloop.IOLoop.current().start() #"""

    #""" ### Ready work
    #server = tornado.httpserver.HTTPServer(ws_app)
    #server.listen(8000, address="0.0.0.0") # omit address

    server = tornado.httpserver.HTTPServer(ws_app, ssl_options={"certfile": "domain.crt", "keyfile": "domain.key",})
    server.listen(443, address="0.0.0.0")

    #tornado.ioloop.IOLoop.current().add_callback(print_changes)
    tornado.ioloop.IOLoop.current().add_callback(sendDesktop)
    #tornado.ioloop.IOLoop.current().add_callback(watch_chats)
    tornado.ioloop.IOLoop.instance().start() #"""

    """ ### Development
    from livereload import Server, shell
    wsgi_app = tornado.wsgi.WSGIAdapter(ws_app)
    server = Server(wsgi_app)
    # livereload on another port
    #server.serve(liveport=35729)

    # use custom host and port
    server.serve(port=8000, host='localhost')

    # open the web browser on startup
    #server.serve(open_url=True, debug=False) #"""

#https://github.com/rethinkdb/docs/blob/issue-684-async-docs/2-query-language/asynchronous.md#python-and-tornado
#https://github.com/rethinkdb/rethinkdb/issues/2622
#https://github.com/hustlzp/Flask-Boost
#https://stackoverflow.com/questions/11694124/tornado-write-a-jsonp-object
#self.write(self.render_string('index.html', ...)).
#https://impythonist.wordpress.com/2015/08/02/build-a-real-time-data-push-engine-using-python-and-rethinkdb/
#http://www.tornadoweb.org/en/stable/guide/templates.html
#https://impythonist.wordpress.com/2015/08/02/build-a-real-time-data-push-engine-using-python-and-rethinkdb/
#http://www.tornadoweb.org/en/stable/guide/running.html#debug-mode # balancer
#https://stackoverflow.com/questions/24851422/serving-images-dynamically-via-stringio-bytesio-in-tornado-templates #write BytesIO
#https://stackoverflow.com/questions/24286618/serving-images-using-tornado-without-file-i-o # write image
#openssl req -newkey rsa:2048 -nodes -keyout domain.key -x509 -days 365 -out domain.crt #true
#openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365
#openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days XXX
#openssl req -key domain.key -new -x509 -days 365 -out domain.crt
###------------------------------------------------
#openssl genrsa -out server.key 2048
#openssl rsa -in server.key -out server.key
#openssl req -sha256 -new -key server.key -out server.csr -subj '/CN=localhost'
#openssl x509 -req -sha256 -days 365 -in server.csr -signkey server.key -out server.crt
###------------------------------------------------
#https://www.digitalocean.com/community/tutorials/openssl-essentials-working-with-ssl-certificates-private-keys-and-csrs
#https://stackoverflow.com/questions/10175812/how-to-create-a-self-signed-certificate-with-openssl

#http://aybabtu.dk/blog/sending-an-image-through-websockets/
#http://laht.info/sending-images-over-websockets-in-python-2-7/
#https://stackoverflow.com/questions/9546437/how-send-arraybuffer-as-binary-via-websocket # send image
#https://www.browserling.com/tools/js-minify
#https://www.rethinkdb.com/api/python/changes/
#https://rethinkdb.com/docs/changefeeds/python/
#https://rethinkdb.com/api/python/wait/
