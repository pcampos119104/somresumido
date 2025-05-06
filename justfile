# List all just commands
default:
  just --list

# Build the docker image
build:
  docker compose build

# Run the Django app in development mode
run:
  docker compose up --build

# Enter in the container shell
shell:
  docker compose run --rm web sh

# Run manage.py inside the container
mng command:
  docker compose run --rm web python manage.py {{command}}

# Run the tests
test:
  docker compose run --rm web ruff check
  docker compose run --rm web pytest

# Run Ruff for fix errors
format:
  docker compose run --rm web ruff check --fix
  docker compose run --rm web ruff format

