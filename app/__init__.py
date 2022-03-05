import os
import traceback

from flask import Flask
from flask_staticdirs import staticdirs
from . import api 

app = Flask(__name__)
api.init_app(app, version='1.0.0', title='Flask API Example')

# serve the frontend application from app/public
public = os.path.join(os.path.dirname(__file__), 'public')
app.register_blueprint(staticdirs(public))

@app.errorhandler(500)
def internal_error(error):
  traceback.print_exc()
  return 500, "Internal Server Error"
