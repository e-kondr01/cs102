import argparse
import async_http as httpd
import io
import logging
import multiprocessing
import sys

from datetime import datetime


class AsyncWSGIServer(httpd.AsyncServer):

    def set_app(self, application):
        self.application = application

    def get_app(self):
        return self.application

    def handle_accepted(self, sock, addr):
        #  log.debug(f"Incoming connection from {addr}")
        print(f"Incoming connection from {addr}")
        AsyncWSGIRequestHandler(sock, self.application)


class AsyncWSGIRequestHandler(httpd.AsyncHTTPRequestHandler):

    def __init__(self, sock, application):
        httpd.AsyncHTTPRequestHandler.__init__(self, sock)
        self.application = application

    def get_environ(self):
        env = {}
        env['wsgi.version'] = (1, 0)
        env['wsgi.url_scheme'] = 'http'
        env['wsgi.input'] = io.StringIO(self.in_buffer)
        env['wsgi.errors'] = sys.stderr
        env['wsgi.multithread'] = False
        env['wsgi.multiprocess'] = True
        env['wsgi.run_once'] = False
        env['REQUEST_METHOD'] = self.method
        env['PATH_INFO'] = self.url
        env['SERVER_NAME'] = '127.0.0.1'
        env['SERVER_PORT'] = '9000'
        return env

    def found_terminator(self):
        self.parse_headers()
        self.parse_request()
        self.handle_request()

    def start_response(self, status, response_headers, exc_info=None):
        curr_time = str(datetime.today())
        server_headers = [
            ('Date', curr_time),
            ('Server', 'async_wsgi_Kondrashov'),
        ]
        self.headers_list = [status, response_headers + server_headers]

    def handle_request(self):
        env = self.get_environ()
        result = self.application(env, self.start_response)

        self.finish_response(result)

    def finish_response(self, result):
        try:
            status, response_headers = self.headers_list
            response = f'HTTP/1.1 {status}\r\n'
            for header in response_headers:
                response += '{0}: {1}\r\n'.format(*header)
            response += '\r\n'
            for data in result:
                response += data.decode('utf-8')
            print(response)
            response_bytes = response.encode()
            self.fixed_push_with_producer(response_bytes)
        finally:
            self.handle_close()


def parse_args():
    parser = argparse.ArgumentParser("Simple asynchronous web-server")
    parser.add_argument('--app', dest='application', default='')
    parser.add_argument("--host", dest="host", default="127.0.0.1")
    parser.add_argument("--port", dest="port", type=int, default=9000)
    parser.add_argument("--log", dest="loglevel", default="debug")
    parser.add_argument("--logfile", dest="logfile", default="wsgi_logs.txt")
    parser.add_argument("-w", dest="nworkers", type=int, default=1)
    parser.add_argument("-r", dest="document_root", default=".")
    return parser.parse_args()


def run(args, application):
    server = AsyncWSGIServer(host=args.host, port=args.port)
    server.set_app(application)
    server.serve_forever()


if __name__ == '__main__':
    args = parse_args()

    if not args.application:
        raise Exception('Provide a WSGI application object as module:callable')
    module, application = args.application.split(':')
    module = __import__(module)
    application = getattr(module, application)

    '''
    logging.basicConfig(
        filename=args.logfile,
        level=getattr(logging, args.loglevel.upper()),
        format="%(name)s: %(process)d %(message)s")
    log = logging.getLogger(__name__)
    '''

    for _ in range(args.nworkers):
        p = multiprocessing.Process(target=run(args, application))
        p.start()
