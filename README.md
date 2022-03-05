# Flask API Example

This is an example of a flask app that:

- exposes a REST API at /api/v1/*
- provides authentication header verfication for accessing /api/v1/*
- exposes a Swagger UI at /api/ui
- serves a frontend application from app/public

This example also shows how to one might deploy the applicaiton to a Kuberntes cluster

- provides a Dockerfile for creating a container image
- provides an NGINX configuration that can wrap access to the container with https


## Development

Assuming you have **Python 3** installed, you can quickly start a local server with:

```
pip install -r requirements.txt
python app
```

Then visit [http://localhost:5000]() with a browser.

### Code Layout

Although there are many ways to layout a Flask applicaiton and the routes, this is my prefered layout.

* `app` - the application source
* `app/__main__.py` - the main entry point for development
* `app/__init__.py` - the Flask applicaiton instance
* `app/api/__init__.py` - defines init_app to register api and swagger ui
* `app/api/swagger.py` - swagger configuration
* `app/api/v1/*.py` - individual sets of api endpoints (flask blueprints)
* `app/api/apispec.yaml` - [OpenAPI](https://www.openapis.org/) specification with shared definitions.

**Note:** these files are related to authentication/authorization and are not yet working:

* `app/api/decorators.py` - used to decorate routes that require auth
* `app/api/keypair.py` - used to sign and verify JWT tokens
* `app/api/auth_token.py` - used to exchange a login code for a JWT token

The main entrypoint is `app/__index__.py`. It initializes the flask app, applies the api blueprints, and the _flasgger_ configuration.

### Extending the api

Each of the `*.py` files under `app/api/v1` creates a Flask blueprint named app. This way you can add calls easily.
Each endpoint has a python docstring (a triple-quoted-string) that contains a partial OpenAPI spec used by Flasgger for the API UI.

The idea is that you can can create a new file under `app/api/v1` and it will automatically be included in the API, no import
or initialization required (via `app/api/__init__.py` called by `app/__init__.py`).

In general, I prefer a functional approach over Classes so I avoid _flask_restful.Resource_.

### Schema Validation

The request validation pattern I use validates json objects against the OpenAPI spec in the docstring of the routes.
See `app/api/v1/todo.py` for an example.

I found this preferrable to using `flasgger.validate()` directly, since it requires the path to a yaml file. I want
to use the schema initilized with the swagger instance, but because of the way I'm using blueprints, it's not
straightfoward to use `swagger.validate()` either.

## Thoughts on Deployment

I have been deploying apps with [Docker](https://www.docker.com/) and [Kubernetes](https://kubernetes.io/) for a while now.
Although I haven't used it, Google has a hosted Kubernetes solution that I think would be a good option for a scalable architecture:
[Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine).

If you have `docker` installed, you can build and run the application in a container:

```
docker build -t flask-api-example .
docker run -it --rm -p 5000:80 flask-api-example
```

Then visit [http://localhost:5000]() with a browser.

If you have `kubectl` installed and are configured (see `kubectl config use-context`), you can deploy

```
docker context create docker-desktop
kubectl config use-context docker-desktop
kubectl apply -f k8s.yaml
kubectl port-forward service/my-flask-api 5000:http
```

Then visit [http://localhost:5000]() with a browser.
