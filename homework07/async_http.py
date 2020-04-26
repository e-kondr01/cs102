import asyncore
import asynchat
import socket
import multiprocessing
import logging
import mimetypes
import os
import argparse
import urllib
import codecs

from datetime import datetime
from pathlib import Path
from time import strftime, gmtime


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
    path = path.replace('%20', ' ')
    return path


'''
class FileProducer(object):

    def __init__(self, f, chunk_size=4096):
        self.file = f
        print(self.file)
        self.chunk_size = chunk_size

    def more(self):
        if self.file:
            print('yes')
            f = open('C:\\cs102\\homework07\\index.html', 'rb')
            data = f.read()
            #data = self.file.read()
            print(data)
            if data:
                return data
            self.file = None
        return ""
'''


class simple_producer:

    def __init__(self, data, buffer_size=512):
        self.buffer_size = buffer_size
        if data:
            self.data = data
            print(f'Data to send: {self.data}')

    def more(self):
        if len(self.data) > self.buffer_size:
            result = self.data[:self.buffer_size]
            self.data = self.data[self.buffer_size:]
            return result
        else:
            result = self.data
            self.data = ''
            return result


class AsyncServer(asyncore.dispatcher):

    def __init__(self, host="127.0.0.1", port=9000):
        super().__init__()
        self.create_socket()
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
        print(f'Server started at: {host}:{port}')

    def handle_accepted(self, sock, addr):
        #  log.debug(f"Incoming connection from {addr}")
        print(f"Incoming connection from {addr}")
        AsyncHTTPRequestHandler(sock)

    def serve_forever(self):
        asyncore.loop()


class AsyncHTTPRequestHandler(asynchat.async_chat):

    def __init__(self, sock):
        super().__init__(sock)
        self.in_buffer = ''
        self.out_buffer = b''
        self.set_terminator(b"\r\n\r\n")

        self.reading_headers = True
        self.handling = False
        self.headers = {}

    def collect_incoming_data(self, data):
        #  log.debug(f"Incoming data: {data}")
        print(f"Incoming data: {data}")
        self.in_buffer += data.decode('ASCII')

    def found_terminator(self):
        if self.reading_headers:
            self.reading_headers = False
            self.parse_headers()
            self.in_buffer = ''
            self.handling = True
            self.parse_request()
        elif self.handling:
            self.parse_request()

    def parse_request(self):
        self.root = Path.cwd() / 'homework07'
        print('URL: ', self.url)
        parsed_url = self.translate_path()
        print(parsed_url)
        self.path = parsed_url[2] if parsed_url[2] else '/'
        self.handle_request()

    def parse_headers(self):
        unparsed = "".join(self.in_buffer)
        headers_lst = unparsed.split('\r\n')
        if 'HEAD' in headers_lst[0]:
            self.method = 'HEAD'
        elif 'GET' in headers_lst[0]:
            self.method = 'GET'
        self.url = headers_lst[0][headers_lst[0].find(' ')+2:headers_lst[0].rfind(' ')]
        for header in headers_lst[1:]:
            key, value = header.split(': ')
            self.headers[key] = value
        print(f'Headers parsed: \n {self.headers}')

    def handle_request(self):
        if self.path.endswith('/'):
            try:
                if self.path == '/':
                    test_path = self.root / 'index.html'
                else:
                    test_path = self.root / self.path / 'index.html'
                f = open(test_path, mode='rb')
                self.path = test_path
                f.close()
            except FileNotFoundError:
                try:
                    test_path = self.root / self.path
                    f = open(test_path, mode='rb')
                    #  File shouldn't open if it ends with '/'
                    self.send_error(404)
                    f.close()
                    return

                except PermissionError:
                    self.send_error(403)
                    return
        else:
            self.path = self.root / self.path
        print(f'Parsed path: {self.path}')

        if self.method == 'GET':
            self.do_GET()
        elif self.method == 'HEAD':
            self.do_HEAD()
        else:
            self.send_error(405)
            self.handle_close()

    def add_header(self, keyword, value):
        self.out_buffer += f'{keyword}: {value}\r\n'.encode()

    def send_error(self, code, message=None):
        print(f'\nError {code}! \n')
        try:
            short_msg, long_msg = responses[code]
        except KeyError:
            short_msg, long_msg = '???', '???'
        if not message:
            message = short_msg

        self.out_buffer = b''
        self.add_response(code, message)
        self.add_header("Content-Type", "text/plain")
        self.add_header("Connection", "close")
        self.end_headers()
        self.push_with_producer(simple_producer(self.out_buffer))
        self.handle_close()

    def add_response(self, code: int, message=None):
        self.out_buffer += f'HTTP/1.1 {code} {responses[code]}\r\n'.encode()

    def end_headers(self):
        self.out_buffer += f'\r\n'.encode()

    def date_time_string(self):
        pass

    def add_head(self):
        curr_time = datetime.now().time()
        self.add_header('Server', 'async_http_py_Kondrashov')
        self.add_header('Date', curr_time)
        self.add_header('Content-Length', self.content_length)
        self.end_headers()

    def translate_path(self):
        url = url_normalize(self.url)
        print(f'Normalized URL: {url}')
        return urllib.parse.urlparse(url)

    def do_GET(self):
        try:
            f = open(self.path, 'rb')
        except FileNotFoundError:
            self.send_error(404)
            return
        data = f.read()
        self.content_length = len(data)
        self.add_response(200)
        self.add_head()
        self.out_buffer += data
        f.close()
        self.push_with_producer(simple_producer(self.out_buffer))
        self.handle_close()
        print('GET completed \n')

    def do_HEAD(self):
        try:
            f = open(self.path, 'rb')
        except FileNotFoundError:
            self.send_error(404)
            return
        data = f.read()
        self.content_length = len(data)
        self.add_response(200)
        self.add_head()
        f.close()
        self.push_with_producer(simple_producer(self.out_buffer))
        self.handle_close()
        print('Head completed \n')


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
