import asyncore
import asynchat
import socket
import multiprocessing
import logging
import mimetypes
import os
import argparse

from datetime import datetime
from pathlib import Path
from time import strftime, gmtime
from urllib.parse import urlparse


def url_normalize(path):
    if path.startswith("."):
        path = "/" + path
    while "../" in path:
        p1 = path.find("/..")
        p2 = path.rfind("/", 0, p1)
        if p2 != -1:
            path = path[:p2] + path[p1+3:]
        else:
            path = path.replace("/..", "", 1)
    path = path.replace("/./", "/")
    path = path.replace("/.", "")
    return path


class FileProducer(object):

    def __init__(self, file, chunk_size=4096):
        self.file = file
        self.chunk_size = chunk_size

    def more(self):
        if self.file:
            data = self.file.read(self.chunk_size)
            if data:
                return data.encode()
            self.file.close()
            self.file = None
        return ""


class AsyncServer(asyncore.dispatcher):

    def __init__(self, host="127.0.0.1", port=9000):
        super().__init__()
        self.create_socket()
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accepted(self, sock, addr):
        #  log.debug(f"Incoming connection from {addr}")
        print(f"Incoming connection from {addr}")
        AsyncHTTPRequestHandler(sock)

    def serve_forever(self):
        asyncore.loop()


class AsyncHTTPRequestHandler(asynchat.async_chat):

    def __init__(self, sock):
        super().__init__(sock)
        self.ibuffer = []
        self.reading_headers = True
        self.handling = False
        self.set_terminator(b"\r\n\r\n")
        self.curr_request = ''
        self.method = 'undefined'
        self.headers = {}
        self.url = None
        self.path = None

    def collect_incoming_data(self, data):
        #  log.debug(f"Incoming data: {data}")
        print(f"Incoming data: {data}")
        self.ibuffer.append(data.decode('ASCII'))

    def found_terminator(self):
        if self.reading_headers:
            self.reading_headers = False
            self.parse_headers()
            self.ibuffer = []
            self.handling = True
            self.parse_request()
        elif self.handling:
            self.parse_request()

    def parse_request(self):
        print('URL: ', self.url)
        parsed_url = self.translate_path()
        print(parsed_url)
        self.path = parsed_url[2]
        if self.path == '/':
            self.path = 'index.html'
        self.handle_request()

    def parse_headers(self):
        unparsed = "".join(self.ibuffer)
        headers_lst = unparsed.split('\r\n')
        if 'HEAD' in headers_lst[0]:
            self.method = 'HEAD'
        elif 'GET' in headers_lst[0]:
            self.method = 'GET'
        self.url = headers_lst[0][headers_lst[0].find(' ')+1:headers_lst[0].rfind(' ')]
        for header in headers_lst[1:]:
            key, value = header.split(': ')
            self.headers[key] = value
        print(f'Headers parsed: \n {self.headers}')

    def handle_request(self):
        if self.method == 'GET':
            self.do_GET()
        elif self.method == 'HEAD':
            self.do_HEAD()
        else:
            self.send_error(405)
            self.handle_close()

    def send_header(self, keyword, value):
        self.push(f'{keyword}: {value}\r\n'.encode())

    def send_error(self, code, message=None):
        try:
            short_msg, long_msg = self.responses[code]
        except KeyError:
            short_msg, long_msg = '???', '???'
        if message is None:
            message = short_msg

        self.send_response(code, message)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Connection", "close")
        self.end_headers()

    def send_response(self, code: int, message=None):
        self.push(f'HTTP/1.1 {code} {responses[code]}\r\n'.encode())

    def end_headers(self):
        self.push(f'\r\n'.encode())

    def date_time_string(self):
        pass

    def send_head(self):
        curr_time = datetime.now().time()
        self.send_header('Server', 'async_http_py_Kondrashov')
        self.send_header('Date', curr_time)
        self.send_header('Content-Length', self.content_length)
        self.end_headers()

    def translate_path(self):
        url = url_normalize(self.url)
        print(f'Normalized URL: {url}')
        return urlparse(url)

    def do_GET(self):
        f = open('C:\\cs102\\homework07\\index.html', 'r')
        f_f = f.readline()
        print(f_f)
        self.content_length = len(f_f)
        print(self.content_length)
        self.send_response(200)
        self.send_head()
        #  p = Path('.')
        pp = self.path
        self.push_with_producer(FileProducer(f))
        print('pushed')
        f.close()
        self.handle_close()
        print('GET is done')

    def do_HEAD(self):
        self.send_response(200)
        self.send_head()
        self.handle_close()
        print('HEAD is done')


responses = {
    200: ('OK', 'Request fulfilled, document follows'),
    400: ('Bad Request',
          'Bad request syntax or unsupported method'),
    403: ('Forbidden',
          'Request forbidden -- authorization will not help'),
    404: ('Not Found', 'Nothing matches the given URI'),
    405: ('Method Not Allowed',
          'Specified method is invalid for this resource.'),
}


def parse_args():
    parser = argparse.ArgumentParser("Simple asynchronous web-server")
    parser.add_argument("--host", dest="host", default="127.0.0.1")
    parser.add_argument("--port", dest="port", type=int, default=9000)
    parser.add_argument("--log", dest="loglevel", default="info")
    parser.add_argument("--logfile", dest="logfile", default="server_logs.txt")
    parser.add_argument("-w", dest="nworkers", type=int, default=1)
    parser.add_argument("-r", dest="document_root", default=".")
    return parser.parse_args()


def run(args):
    server = AsyncServer(host=args.host, port=args.port)
    server.serve_forever()


if __name__ == "__main__":
    args = parse_args()

    ''' logging.basicConfig(
        filename=args.logfile,
        level=getattr(logging, args.loglevel.upper()),
        format="%(name)s: %(process)d %(message)s")
    log = logging.getLogger(__name__) '''

    DOCUMENT_ROOT = args.document_root
    for _ in range(args.nworkers):
        p = multiprocessing.Process(target=run(args))
        p.start()
