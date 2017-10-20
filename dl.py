import os
import tempfile
import tornado.httpclient
import tornado.ioloop

class HttpDownload(object):
  def __init__(self, url, ioloop):
    self.ioloop = ioloop
    self.tempfile = tempfile.NamedTemporaryFile(delete=False)
    req = tornado.httpclient.HTTPRequest(
        url = url,
        streaming_callback = self.streaming_callback)
    http_client = tornado.httpclient.AsyncHTTPClient()
    http_client.fetch(req, self.async_callback)

  def streaming_callback(self, data):
    self.tempfile.write(data)

  def async_callback(self, response):
    self.tempfile.flush()
    self.tempfile.close()
    if response.error:
      print( "Failed")
      os.unlink(self.tempfile.name)
    else:
      print("Success: %s" % self.tempfile.name)
      self.ioloop.stop()

def main():
  ioloop = tornado.ioloop.IOLoop.instance()
  dl = HttpDownload("http://codingrelic.geekhold.com/", ioloop)
  ioloop.start()

if __name__ == '__main__':
  main()

#with open(output_file_name) as f:
  #f.write(response.body)
