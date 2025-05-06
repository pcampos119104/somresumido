# somresumido project

Project crated using Copier tool.

## Tools, libs, etc. Some time related files.

Versions on Poetry.

- [Python](https://www.python.org/) Programming languange
- [django-environ](https://django-environ.readthedocs.io) Manage .envs in Django
- [Poetry](https://python-poetry.org/) Python packaging and dependency management
    - poetry.lock
    - pyproject.toml
- [Django](https://www.djangoproject.com/) Web framework written in Python
- [Docker](https://www.docker.com/) Manage containers for dev environment
    - compose.yaml
    - compose/dev/Dockerfile
    - compose/dev/start
    - .env
- [Just](https://just.systems/) Encapsulate commands for easier use
    - justfile
- [psycopg](https://www.psycopg.org/) Python adapter for Postgres
- [AlpineJS](https://alpinejs.dev/) JavaScript Framework based on Vue
- [PicoCSS](https://picocss.com/) CSS Framework
- [HTMX](https://htmx.org/) htmx give access to AJAX, CSS Transitions, WebSockets and Server Sent Events directly from HTML
- [django-extensions](https://django-extensions.readthedocs.io/en/latest/) Add manage commands to the django and more 

### ...and development

- [django-browser-reload](https://github.com/adamchainz/django-browser-reload) Auto reload the browser when change a template 
- [ruff](https://docs.astral.sh/ruff/) Linter and code formater 
- [Pytest](https://docs.pytest.org/en/8.0.x/) Tools for testing.
- [Pytest-django](https://pytest-django.readthedocs.io/en/latest/) Pytest Plugin for Django
- [Marimo](https://marimo.io/) Notebook for test, prototype, inspections, etc.
  - local/template.py - Template for a new notebook.
## Dev environment setup

1. Install Just, Docker and Poetry(opcional).
2. Copie .env.example to .env, no need for edtion. 
3. `$ just build`

## Run the server for development

1. Certified that docker is up and running
2. `$ just runserver`

You can access the Django app on http://0.0.0.0:8000/ and Marimo notebook on http://0.0.0.0:2718/

## On production
add to the .env:

ALLOWED_HOSTS=somresumido.pcampos.com.br
CSRF_TRUSTED_ORIGINS=https://somresumido.pcampos.com.br
