from http.client import HTTPException
import os
import flasgger
import pkg_resources
import yaml
import logging
from flask import abort, jsonify, make_response

logger = logging.getLogger()

_swagger = None

# this will be the Swagger instance's validate method
def validate(data, schema_id, code=400, *args, **kwargs):
  global _swagger
  if _swagger is None:
    abort(500, 'Schema validation not ready')
  
  def error_handler(err, data, main_def):
    abort(make_response(jsonify(error=f'Schema validation failed', data=data, details=str(err)), code))

  apispecs = _swagger.get_apispecs()
  return flasgger.validate(data, schema_id, specs=apispecs, validation_error_handler=error_handler, *args, **kwargs)

def init_app(app, title='API', version='1.x.x', spec='apispec.yaml'):
  app.config['SWAGGER'] = {
    'title': title,
    'uiversion': 3,
    'specs_route': '/api/ui',
    'openapi': '3.0.0',
    'static_url_path': '/api/static',
  }

  template = {}
  try:
    global apispec
    apispec = os.path.join(os.path.dirname(__file__), spec)
    template = yaml.safe_load(pkg_resources.resource_stream(__package__, spec))
  except FileNotFoundError as e:
    logger.warn(str(e))
  except yaml.parser.ParserError as e:
    logger.warn(f'Could not parse {spec}: ' + str(e))

  template['info'] = {
    'title': title,
    'version': version
  }
  global _swagger
  _swagger = flasgger.Swagger(app, template=template)
  return _swagger