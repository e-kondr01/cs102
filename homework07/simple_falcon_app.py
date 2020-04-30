import falcon
import json


class QuoteResource:

    def on_get(self, req, resp):
        quote = {
            'quote': 'I\'ve always been more interested in the future than in the past.',
            'author': 'Grace Hopper'
        }
        resp.body = json.dumps(quote)

    def on_post(self, req, resp):
        pass


app = falcon.API()
app.add_route('/quote', QuoteResource())
