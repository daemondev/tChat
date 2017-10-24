import rethinkdb as r
from datetime import datetime

conn = r.connect(host='localhost', port=28015, db='chat')

n = 0
new_chat = None
def ins():
    """Insert a new chat"""
    global n
    n = n + 1
    data = {'name':'RethinkDB', 'message':'(%d .-) FROM SERVER' % n, 'created':str(datetime.now(r.make_timezone('00:00')))}
    new_chat = r.table("chats").insert([ data ]).run(conn)

def drop():
    """Delete all chats (truncate)"""
    r.db('chat').table('chats').delete().run(conn)

def sb():
    data = {'action':'start', 'status':1}
    new_chat = r.table("botActions").insert([ data ]).run(conn)

#drop()
#ins()
sb()
