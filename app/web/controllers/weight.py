import cherrypy

import app.models
from app.config import Config


class Weight():
    def __init__(self):
        self.index_template = Config.jinja_env.get_template('weight/index.html')

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    def index(self):
        chinchillas = app.models.Chinchilla.all()
        params = {'chinchillas': chinchillas}
        return self.index_template.render(params)
