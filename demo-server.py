#!/usr/bin/env -S python3 -W ignore -u

"""
Python Web Server
"""

import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
import argparse
import daemon
import signal
from cbcmgr.cb_operation_s import CBOperation
from functools import partial
from google_embedding import GoogleEmbedding
from restmgr import RESTManager

PORT_NUMBER = 8080
LOG_FILE = 'service.log'

MAIN_PAGE = b"""
   <form method = 'POST' action="search">
      <label for="question" style="font-size: 30px;">Describe a movie:</label>
      <input type="text" id="question" name="question" class="input-area"><br>
      <p><button>Get Results</button></p>
   </form>
"""

RESULTS_HEAD = b"""
<!DOCTYPE html>
<html>
<head>
  <title>Movie Results</title>
  <style type="text/css">
  html, body {
    height: 100%;
  }

  html {
    display: table;
    margin: auto;
  }

  body {
    display: table-cell;
    vertical-align: middle;
    font-family: Arial, sans-serif;
  }
  
  button {
    background-color: #0096FF; /* Green */
    border: none;
    color: white;
    padding: 15px 32px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 24px;
    border-radius: 12px;
  }
  
  .input-area{
    width: 500px;
    height: 40px;
    font-size: 24px;
  }
  </style>
</head>
<body>
"""

RESULTS_TAIL = b"""
</body>
</html>
"""


class WebServer(BaseHTTPRequestHandler):

    def __init__(self, db, *args, **kwargs):
        self.db = db
        super().__init__(*args, **kwargs)

    def forbidden(self):
        self.send_response(403)
        self.send_header("Content-type", 'text/html')
        self.end_headers()
        self.wfile.write(b'<html>Forbidden</html>')

    def server_error(self):
        self.send_response(500)

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(RESULTS_HEAD)
            self.wfile.write(MAIN_PAGE)
            self.wfile.write(RESULTS_TAIL)
        elif self.path == '/favicon.ico':
            self.send_response(200)
            self.send_header('Content-type', 'image/x-icon')
            self.end_headers()
            image_bytes = RESTManager().get_url_content('https://docs.couchbase.com/_/img/favicon.ico')
            self.wfile.write(image_bytes)
        elif self.path == '/healthz':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html>READY</html>')
        else:
            self.forbidden()

    def do_POST(self):
        if self.path == '/search':
            content_length = int(self.headers['Content-Length'])
            post_data_bytes = self.rfile.read(content_length)

            post_data_str = post_data_bytes.decode("UTF-8")
            list_of_post_data = post_data_str.split('&')

            post_data_dict = {}
            for item in list_of_post_data:
                variable, value = item.split('=')
                post_data_dict[variable] = value

            vector = GoogleEmbedding().get_text_embeddings(post_data_dict['question'].replace('+', ' '))

            results = self.db.vector_search('movie_vector', 'image_embedding', vector)

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(RESULTS_HEAD)
            for result in results:
                self.wfile.write(result.get('title').encode("UTF-8"))
                self.wfile.write(b'<br>')
                self.wfile.write(f"<img src=\"{result.get('poster_path')}\" height=\"600\">".encode("UTF-8"))
                self.wfile.write(b'<br>')
            self.wfile.write(b'<a href="/">Home</a>')
            self.wfile.write(RESULTS_TAIL)


class ServerHandler(object):

    def __init__(self, host, port, db):
        self.hostname = host
        self.port = port
        handler = partial(WebServer, db)
        self.server = HTTPServer((self.hostname, self.port), handler)

    def start(self):
        self.server.serve_forever()

    def stop(self):
        self.server.server_close()


def parse_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-d', '--daemon', action='store_true')
    parser.add_argument('-P', '--port', action='store', default=PORT_NUMBER)
    parser.add_argument('-l', '--log', action='store', default=LOG_FILE)
    parser.add_argument('-u', '--user', action='store', help="User Name", default="Administrator")
    parser.add_argument('-p', '--password', action='store', help="User Password", default="password")
    parser.add_argument('-h', '--host', action='store', help="Cluster Node Name", default="localhost")
    parser.add_argument('-b', '--bucket', action='store', help="Bucket", default="movies")
    parser.add_argument('-s', '--scope', action='store', help="Scope", default="data")
    parser.add_argument('-c', '--collection', action='store', help="Collection", default="data")
    parser.add_argument('-?', action='help')
    args = parser.parse_args()
    return args


def main():
    options = parse_args()

    print(f"Starting Service: [User] {options.user} [Bucket] {options.bucket}")

    keyspace = f"{options.bucket}.{options.scope}.{options.collection}"
    op = CBOperation(options.host, options.user, options.password, ssl=True, quota=1024, create=True, replicas=0)
    op.connect(keyspace)

    server = ServerHandler('127.0.0.1', options.port, op)
    logfile = open(options.log, 'w')

    def signal_handler(signum, frame):
        server.stop()
        sys.exit(0)

    if options.daemon:
        context = daemon.DaemonContext(stdout=logfile, stderr=logfile)
        context.files_preserve = [server.server.fileno()]
        context.signal_map = {
            signal.SIGTERM: signal_handler,
            signal.SIGINT: signal_handler,
        }
        with context:
            server.start()
    else:
        signal.signal(signal.SIGINT, signal_handler)
        server.start()


if __name__ == '__main__':
    try:
        main()
    except SystemExit as e:
        sys.exit(e.code)
