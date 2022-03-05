import os
import jwt
from functools import wraps
from flask import abort, request, globals


def getenv_array(name, plural, default=''):
  return map(lambda x: x.strip(), (os.getenv(name) or os.getenv(plural) or default).split(','))


API_KEYS = getenv_array('API_KEY', 'API_KEYS')
JWKS_URI = os.getenv('JWKS_URI')


if JWKS_URI:
  jwks_client = jwt.PyJWKClient(JWKS_URI)
jwt_signing_key = None
jwt_signing_algorithms = getenv_array('JWT_ALGORITHM', 'JWT_ALGORITHMS', 'RS256')


def set_jwt_signing_key(key, algorithms=jwt_signing_algorithms):
  """ Set the jwt signing options """
  global jwt_signing_key
  global jwt_signing_algorithms
  jwt_signing_key = key
  jwt_signing_algorithms = algorithms


def requires_auth(func):
  """ Ensures the request includes valid authorization

  This checks that the request includes a valid API Key or JSON Web Token.

  Example:
      If the API_KEY or API_KEYS env var is specified, it will contain a comma-separated list of
      valid API Keys. The request should include the API Key in the request header:

          X-API-Key: 8f9dac00-f283-4249-a0fb-225b47baecd2

      Note: this behavior could be modified to lookup API Keys from a database.

      If the JWKS_UIR env var is specified, the function will validate a JSON Web Token's
      signature using keys provided by that URI. The request should include a JWT
      provided as a Bearer token inthe request header:

          Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c

      The list of acceptable signing algorithms are specired as a comma-separated list in the
      JWT_ALGORITHM or JWT_ALGORITHMS env vars. The default is 'RS256'.
  """
  @wraps(func)
  def decorated_func(*args, **kwargs):
    authorized = False

    if len(API_KEYS) > 0:
      apikey = request.headers.get('x-api-key')
      if apikey in API_KEYS:
        authorized = True

    if JWKS_URI is not None or jwt_signing_key is not None:
      auth = request.headers.get('authorization')
      if auth is not None:
        a = auth.split(' ',1)
        if a[0].lower() != 'bearer' or len(a) != 2:
          abort(401, 'Malformed Authorization')
        token = a[1]
        try:
          if jwt_signing_key is not None:
            globals.jwt = jwt.decode(token, jwt_signing_key, algorithms=jwt_signing_algorithms)
          elif JWKS_URI is not None:
            signing_key = signing_key or jwks_client.get_signing_key_from_jwt(token)
            globals.jwt = jwt.decode(token, signing_key.key, algorithms=jwt_signing_algorithms)
          authorized = True
        except jwt.exceptions.ExpiredSignatureError:
          abort(401, 'Expired Token')
        except jwt.exceptions.InvalidTokenError:
          abort(401, 'Invalid Token')

    if not authorized:
      abort(401, 'Not Authorized')

    return func(*args, **kwargs)
  return decorated_func


@requires_auth
def requires_rights(*rights, any=False):
  """" Ensures that the jwt token describes the listed rights """
  def decorator(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):
      if JWKS_URI is not None or jwt_signing_key is not None:
        granted = globals.jwt.get('rights',[])
        overlap = set.intersection(set(rights), set(granted))
        if (any and len(overlap) < 1) or (len(overlap) != len(rights)):
          abort(403, 'Operation Not Permitted')
      else:
        abort(403, 'Operation Not Permitted')
    return decorated_func
  return decorator