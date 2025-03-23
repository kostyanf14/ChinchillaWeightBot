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
    
    # t = 1
    # for w in [619,619,603,610,607, 595,595,598,582,570,605]:
    #    app.models.Weight(chinchilla_id=1, time = t * 10, weight=w).save()
    #    t = t + 1

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    def show(self, chinchilla_id: str):
        self.show_template = Config.jinja_env.get_template('chinchilla/show.html')
        chinchilla = app.models.Chinchilla.find(int(chinchilla_id))
        weights = app.models.Weight.all_by_chinchilla(chinchilla.id)

        c_times = list(map(lambda w: w.time, weights))
        c_weights = list(map(lambda w: w.weight, weights))

        params = {'chinchilla_name': chinchilla.name, 'c_times': c_times, 'c_weights': c_weights}
        return self.show_template.render(params)
