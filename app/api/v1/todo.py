import uuid
import jsonpatch
from flask import abort, Blueprint, jsonify, request
from datetime import datetime, timezone
from ..swagger import validate

app_name = __name__.split(".")[-1]
app = Blueprint(app_name, app_name)

todos = [] # this example just updates this array, probably should update a database


def find(f, seq):
  """Return first item in sequence where f(item) == True"""
  for item in seq:
    if f(item): 
      return item


@app.route('/api/v1/todos')
def list_entries():
  """ List all todo entries
  ---
  tags:
    - todo
  responses:
    200:
      content:
        application/json:
          schema:
            type: array
            items:
              $ref: '#/definitions/Todo'
  """
  return jsonify(todos)


@app.route('/api/v1/todo/<id>')
def get_entry(id):
  """ Get a todo entry
  ---
  tags:
    - todo
  parameters:
    - name: id
      in: path
      schema: { type: string }
  responses:
    404:
      description: Not Found
    200:
      content:
        application/json:
          schema:
            type: object
            properties:
              note: { type: string }
              due: { type: string, format: date-time }
              done: { type: boolean }
              created: { type: string, format: date-time }
              completed: { type: string, format: date-time }
              last_update: { type: string, format: date-time }
  """
  entry = find(lambda x: x['id'] == id, todos)
  if entry is None:
    abort(404, 'Entry Not Found')
  return jsonify(entry)


@app.route('/api/v1/todo', methods=['POST'])
def create():
  """ Create a new todo entry
  ---
  tags:
    - todo
  requestBody:
    required: true
    content:
      application/json:
        schema:
          id: CreateTodo
          type: object
          properties:
            note: { type: string }
            due: { type: string, format: date-time }
          required: [ note ]

  responses:
    400:
      description: Bad Request
    201:
      content:
        application/json:
          schema:
            $ref: '#/definitions/Todo'
  """
  json = request.get_json()
  validate(json, 'CreateTodo')
  json['id'] = str(uuid.uuid4())
  json['created'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
  todos.append(json)
  return jsonify(json)


@app.route('/api/v1/todo/<id>', methods=['PUT'])
def update(id):
  """ Update or create a todo entry
  ---
  tags:
    - todo
  parameters:
    - name: id
      in: path
      schema: { type: string }
  requestBody:
    required: true
    content:
      application/json:
        schema:
          $ref: '#/definitions/Todo'

  responses:
    400:
      description: Bad Request
    200:
      content:
        application/json:
          schema:
            $ref: '#/definitions/Todo'
  """
  json = request.get_json()
  validate(json, 'Todo')

  json['id'] = id # reject any id changes
  json['last_updated'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

  entry = find(lambda x: x['id'] == id, todos)
  if entry is not None:
    todos.remove(entry)
  todos.append(json)

  return jsonify(json)


@app.route('/api/v1/todo/<id>', methods=['PATCH'])
def patch(id):
  """ Update a todo entry
  ---
  tags:
    - todo
  parameters:
    - name: id
      in: path
      schema: { type: string }
  requestBody:
    required: true
    content:
      application/json:
        schema:
          type: array
          items:
            oneOf:
              - type: object
                properties:
                  op: { type: string, enum: ['add', 'replace', 'test'] }
                  path: { type: string }
                  value: { }
                required: [ op, path, value ]
              - type: object
                properties:
                  op: { type: string, enum: ['remove', 'replace'] }
                  path: { type: string }
                required: [ op, path ]
              - type: object
                properties:
                  op: { type: string, enum: ['move', 'copy'] }
                  from: { type: string }
                  path: { type: string }
                required: [ op, from, path ]
          example:
            - op: replace
              path: /note
              value: updated note

  responses:
    400:
      description: Bad Request
    404:
      description: Not Found
    422:
      description: Invalid Patch Result
    201:
      description: Test Failed; Patch Not Applied
    200:
      content:
        application/json:
          schema:
            $ref: '#/definitions/Todo'

  """
  json = request.get_json()

  entry = find(lambda x: x['id'] == id, todos)
  if entry is None:
    abort(404, 'Entry Not Found')

  try:
    patch = jsonpatch.JsonPatch(json)
    result = patch.apply(entry)
  except jsonpatch.InvalidJsonPatch as e:
    abort(400, str(e))
  except jsonpatch.JsonPatchConflict as e:
    abort(409, str(e))
  except jsonpatch.JsonPatchTestFailed as e:
    return jsonify(entry), 201

  result['id'] = id # reject any id changes
  result['last_updated'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
  validate(result, 'Todo', 422)
  todos.remove(entry)
  todos.append(result)
  return jsonify(result)


@app.route('/api/v1/todo/<id>', methods=['DELETE'])
def delete(id):
  """ Remove a todo entry
  ---
  tags:
    - todo
  parameters:
    - name: id
      in: path
      schema: { type: string }
  responses:
    204:
      description: Already Removed
    200:
      description: Successfully Removed
      content:
        application/json:
          schema:
            $ref: '#/definitions/Todo'
  """
  entry = find(lambda x: x['id'] == id, todos)
  if entry is None:
    return '', 204
  todos.remove(entry)

  return jsonify(entry)