# Pull official base image
FROM python:3.13.2-alpine3.21

# Set working directory
WORKDIR /app

# Set env variables

# Don't write out pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# No buffering stdin/stdout
ENV PYTHONUNBUFFERED 1

# update the alpine linux
RUN apk update
# install bash on image, could be the ash but the bash is more agnostic
RUN apk add --no-cache bash
RUN apk add --no-cache curl
RUN apk add --no-cache postgresql-client
RUN pip3 install 'xonsh[full]'

# Copy our poetry artifacts to the building image
COPY poetry.lock pyproject.toml /app

RUN pip3 install poetry
# No need to create a virtual env in the container
RUN poetry config virtualenvs.create false
# Install dependencies with the dev dependecies
RUN poetry install --with dev

# Copy start bash script with the instruction on how to start Django.
COPY ./docker/dev/start.xsh /start.xsh
RUN sed -i 's/\r$//g' /start.xsh
RUN chmod +x /start.xsh

# Copy all project to the image.
COPY . /app

# Not used, the app are going to be running through docker compose
CMD ["manage.py", "runserver", "0.0.0.0:8000"]