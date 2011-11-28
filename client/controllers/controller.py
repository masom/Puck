from mako.template import Template
from mako.lookup import TemplateLookup
import cherrypy

class Controller(object):
    '''
    Base controller class.
    Defines functions used by all controllers.
    '''

    def _cp_on_error(self):
        cherrypy.response.body = ("We apologise for the fault in the website. "
                                  "Those responsible have been sacked.")

    lookup = TemplateLookup(directories=['html'])

    @classmethod
    def render(cls, template, **variables):
        variables['flash'] = cherrypy.session.pop('flash', None)
        tmpl = cls.lookup.get_template(template)
        return tmpl.render(**variables)