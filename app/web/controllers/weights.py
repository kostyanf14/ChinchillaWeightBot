import cherrypy

import app.models
from app.config import Config


class Weights():
    def __init__(self):
        self.index_template = Config.jinja_env.get_template('weights/index.html')
        self.edit_template = Config.jinja_env.get_template('weights/edit.html')
        self.new_template = Config.jinja_env.get_template('weights/new.html')

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    def index(self):
        weights = app.models.Weight.all()
        params = { 'weights': weights }
        return self.index_template.render(params)

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    def new(self):
        chinchillas = app.models.Chinchilla.all()
        return self.new_template.render({ 'chinchillas': chinchillas})

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    def edit(self, weight_id: str):
        weight = app.models.Weight.find(int(weight_id))
        chinchillas = app.models.Chinchilla.all()
        return self.edit_template.render({'weight': weight, 'chinchillas': chinchillas})

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    def create(self, chinchilla_id: str, time: str, weight: str):
        rule = app.models.Weight(chinchilla_id=int(chinchilla_id), time=int(time), weight=int(weight))
        rule.save()
        raise cherrypy.HTTPRedirect('/weights')
    
    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    def destroy(self, weight_id: str):
        app.models.Weight.find(int(weight_id)).destroy()
        raise cherrypy.HTTPRedirect('/weights')