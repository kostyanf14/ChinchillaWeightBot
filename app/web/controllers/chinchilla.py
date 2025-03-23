from datetime import datetime
import cherrypy

import app.models
from app.config import Config


class Chinchilla():
    def __init__(self):
        self.index_template = Config.jinja_env.get_template('chinchilla/index.html')
        self.show_template = Config.jinja_env.get_template('chinchilla/show.html')

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    def index(self):
        chinchillas = app.models.Chinchilla.all()
        params = {'chinchillas': chinchillas}
        return self.index_template.render(params)

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    def show(self, chinchilla_id: str):
        self.show_template = Config.jinja_env.get_template('chinchilla/show.html')
        chinchilla = app.models.Chinchilla.find(int(chinchilla_id))
        weights = app.models.Weight.all_by_chinchilla(chinchilla.id)

        c_times = list(map(lambda w: datetime.fromtimestamp(w.time).strftime("%m-%d"), weights))
        c_weights = list(map(lambda w: w.weight, weights))
        min_weight = min(c_weights)
        max_weight = max(c_weights)
        min_weight -= (max(c_weights) - min(c_weights)) // 2
        max_weight += (max(c_weights) - min(c_weights)) // 2

        params = {
            'chinchilla_name': chinchilla.name,
            'c_times': c_times,
            'c_weights': c_weights,
            'min_weight': min_weight,
            'max_weight': max_weight
            }
        return self.show_template.render(params)
