"""Exposes wrapper for user to re-init agent in prefork web servers"""

def post_fork(server, worker):
    """Used to reinitialize exporter & processors in separate worker processes"""
    from hypertrace.agent import Agent  # pylint:disable=C0411,C0415
    server.log.info("Add post hook %s", worker.pid)
    Agent()._init.post_fork()  # pylint:disable=W0212
