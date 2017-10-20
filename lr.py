from livereload import Server, shell

server = Server(wsgi_app)

# run a shell command
server.watch('static/*.stylus', 'make static')

# run a function
def alert():
    print('foo')
server.watch('foo.txt', alert)

# output stdout into a file
server.watch('style.less', shell('lessc style.less', output='style.css'))

server.serve()
