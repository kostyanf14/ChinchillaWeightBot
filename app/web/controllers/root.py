import logging

import cherrypy

from .chinchilla import Chinchilla
from .weight import Weight

logger = logging.getLogger(__name__)


class Root():
    def __init__(self) -> None:
        self.chinchilla = Chinchilla()
        self.weight = Weight()
        logger.debug("Created app controllers")

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("/chinchilla")
