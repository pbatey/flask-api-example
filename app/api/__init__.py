import importlib
import os
from flask import jsonify, request

from . import swagger
from .v1 import auth_token

def blueprint_loader(app, module, ignore=[], bp_name='app', parent=__name__):
    """ Registers blueprints, named bp_name, in any *.py files under {parent}.{module}
    """
    cwd = os.path.join(os.path.dirname(os.path.realpath(__file__)), module)
    for i in list(sorted(os.listdir(f'{cwd}'))):
        if i.endswith('.py') and not i == ('__init__.py') and not i in ignore:
            m_name = i.split('.')[0]
            m = importlib.import_module(f'{parent}.{module}.{m_name}', bp_name)
            app.register_blueprint(getattr(m, 'app'))


def init_app(app, version='1.x.x', title='API', enable_auth_token=False):
  blueprint_loader(app, 'v1', ['auth_token.py'])
  swagger.init_app(app, version=version, title=title)

  if enable_auth_token:
      app.register_blueprint(auth_token)

  @app.errorhandler(400)
  @app.errorhandler(404)
  @app.errorhandler(409)
  @app.errorhandler(422)
  @app.errorhandler(500)
  def http_error_handler(e):
    if request.path.startswith('/api/'):
      return jsonify(error=str(e)), e.code
