import threading
from wsgiref.simple_server import make_server

from tests import find_free_port, setup_custom_logger
logger = setup_custom_logger(__name__)

class FlaskServer(threading.Thread):
    def __init__(self, app):
        super().__init__()
        app.use_reloader = False
        self.daemon = True
        self.port = find_free_port()
        threading.Thread.__init__(self)
        self.srv = make_server('localhost', self.port, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        logger.info('starting server.')
        self.srv.serve_forever()

    def shutdown(self):
        logger.info('Shutting down server.')
        self.srv.shutdown()

