import async_http as httpd
import multiprocessing
import sys


class AsyncWSGIServer(httpd.AsyncServer):

    def set_app(self, application):
        self.application = application

    def get_app(self):
        return self.application


class AsyncWSGIRequestHandler(httpd.AsyncHTTPRequestHandler):

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

    def start_response(self, status, response_headers, exc_info=None):
        curr_time = datetime.now().time()
        server_headers = [
            ('Date', curr_time),
            ('Server', 'async_wsgi_Kondrashov'),
        ]
        self.headers_set = [status, response_headers + server_headers]

    def handle_request(self):
        #request_data = self.in_buffer

        #self.parse_request(request_data)

        env = self.get_environ()
        result = self.application(env, self.start_response)

        self.finish_response(result)

    def finish_response(self, result):
        try:
            status, response_headers = self.headers_set
            response = f'HTTP/1.1 {status}\r\n'
            for header in response_headers:
                response += '{0}: {1}\r\n'.format(*header)
            response += '\r\n'
            for data in result:
                response += data.decode('utf-8')
            response_bytes = response.encode()
            self.fixed_push_with_producer(response_bytes)
        finally:
            self.handle_close()


def application(env, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return [b'Hello World']


def run(application):
    server = AsyncWSGIServer()
    server.set_app(application)
    server.serve_forever()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Provide a WSGI application object as module:callable')
    app_path = sys.argv[1]
    module, application = app_path.split(':')
    module = __import__(module)
    application = getattr(module, application)

    for _ in range(2):
        p = multiprocessing.Process(target=run(application))
        p.start()
