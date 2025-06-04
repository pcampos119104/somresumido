#!/usr/bin/env xonsh
# start.xsh

import os
import time
import subprocess
import sys
from pathlib import Path

# Configurar opções de erro (equivalente a set -e, -o pipefail)
$RAISE_SUBPROC_ERROR = True
$XONSH_TRACEBACK_LOGFILE = '/tmp/xonsh_traceback.log'

# Obter SERVICE_TYPE
service_type = os.environ.get('SERVICE_TYPE', 'web')

# Executar comando baseado em SERVICE_TYPE
match service_type:
    case 'web':
        print("Executando migrações...")
        python manage.py migrate
        print("collectstatic")
        python manage.py collectstatic --no-input
        print("Iniciando servidor Django...")
        execx('gunicorn --bind :80 --workers 3 somresumido.wsgi:application')
    case 'celery':
        print("Iniciando Celery worker...")
        execx('celery -A somresumido worker --loglevel=info -Q celery --concurrency=4')
    case 'rabbitmq_consumer':
        print("Iniciando consumidor RabbitMQ...")
        execx('python -m somresumido.rabbitmq_consumer')
    case _:
        print(f"SERVICE_TYPE inválido: {service_type}")
        sys.exit(1)