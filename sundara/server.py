"""Implements the functionality for the built-in development server.

A tiny little HTTP file server, not suitable for use in production
environments.
"""

import os
import http.server
from urllib.parse import unquote

from sundara import config as sundara_config

class SundaraServer():
    def __init__(self, ip='127.0.0.1', port=8080, config=None):
        if config is None:
            self.ip = ip
            self.port = int(port)
            path = os.path.join(os.getcwd(), 'www')
        else:
            self.ip = config.get('server', 'ip')
            self.port = int(config.get('server', 'port'))
            path = config.get('sundara', 'generate')
        if not os.path.exists(path):
            raise IOError(2, "No such path: %s" % path)

    def run(self):
        print("Starting Sundara development server...")
        httpd = http.server.HTTPServer((self.ip, self.port),
                                        SundaraRequestHandler)
        try:
            print("Server listening on http://%s:%s/" % (self.ip, self.port))
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Server shutting down...")
            httpd.shutdown()


class SundaraRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Implements the functionality for Sundara's built-in development
    server. A tiny little HTTP server, not suitable for use in production
    environments.

    This is an http.server Request Handler.
    """

    def translate_path(self, path):
        """This function overrides that in http.server.SimpleHTTPRequestHandler
        and modifies it to serve files from Sundara's `generate` path
        instead of the cwd.
        """
        path = path.split('?',1)[0]
        path = os.path.normpath(unquote(path))
        words = path.split(os.sep)
        words = filter(None, words)

        if os.path.exists(os.path.join(os.getcwd(), sundara_config.PROJECT_CONF)):
            path = sundara_config.Config(os.getcwd()).get('sundara', 'generate')
        else:
            path = os.path.join(os.getcwd(), 'www/')

        for word in words:
            _, word = os.path.splitdrive(word)
            _, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path
