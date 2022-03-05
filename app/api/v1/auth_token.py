from time import time
from flask import abort, Blueprint, jsonify, request
import jwt

from ..decorators import set_jwt_signing_key
from ..keypair import private_key, public_key

app_name = __name__.split(".")[-1]
app = Blueprint(app_name, app_name)

EXPIRES = 1200 # 20 minutes
ALGORITHM = 'RS256'
set_jwt_signing_key(public_key, [ALGORITHM]) # setup decorator to use self-generated tokens


@app.route('/api/v1/auth/login', methods=['POST'])
def auth_token():
  """ Exchange a code for bearer token
  ---
  tags:
    - auth
  requestBody:
    required: true
    content:
      application/json:
        schema:
          type: object
          properties:
            code: { type: string, rquired: true }
            source: { type: string, enum: ['oauth2', 'google/id_token'] }

  responses:
    200:
      content:
        application/json:
          schema:
            type: object
            properties:
              token: { type: string }
  """
  body = request.get_json() or {}
  code = body.get('code')
  if code is None:
    abort(400, 'code is required')
  source = body.get('source', 'google')

  userid = validateCode(code, source)

  exp = int(time()) + EXPIRES
  sub = userid
  payload = {'exp': exp, 'sub': sub} # you can add rights to the payload than can be checked later
  token = jwt.encode(payload, private_key, ALGORITHM)

  return jsonify({'token':token})


def decode(token):
  try:
    return jwt.decode(token, public_key, ALGORITHM)
  except jwt.ExpiredSignatureError:
    abort(401, 'Authentication token has expired')
  except jwt.InvalidTokenError:
    abort(401, 'Could not validate authentication token')


def validateCode(code, source):
  if not request.headers.get('X-Requested-With'):
    abort(403)

  if source == 'google/id_token':
    credentials = client.credentials_from_clientsecrets_and_code(
    CLIENT_SECRET_FILE,
    ['https://www.googleapis.com/auth/drive.appdata', 'profile', 'email'],
    auth_code)

    return True
