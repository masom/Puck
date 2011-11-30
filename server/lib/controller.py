import cherrypy

from mako.template import Template
from mako.lookup   import TemplateLookup

class Controller(object):
    lookup = TemplateLookup(directories=['views'])
    models = []
    sub = []

    def __init__(self, models):
        for model in self.models:
            setattr(self, model.__name__, models[model])
            
    @classmethod
    def render(cls, template, crumbs=[], **variables):
        tmpl = cls.lookup.get_template(template)
        variables['flash'] = cherrypy.session.pop('flash', None)
        variables['breadcrumbs'] = crumbs
        return tmpl.render(**variables)