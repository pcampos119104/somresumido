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

# Função para aguardar um serviço
def wait_for_service(service_name: str, check_cmd: list, timeout: int = 30, interval: int = 5) -> bool:
    """Aguarda até que o serviço esteja disponível."""
    print(f"Aguardando {service_name}...")
    for attempt in range(timeout // interval):
        try:
            subprocess.run(check_cmd, check=True, capture_output=True, text=True)
            print(f"{service_name} está pronto.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"{service_name} não está pronto, tentativa {attempt + 1}/{timeout // interval}: {e.stderr.strip()}")
            time.sleep(interval)
    print(f"Erro: {service_name} não ficou pronto após {timeout} segundos.")
    return False

# Obter SERVICE_TYPE
service_type = os.environ.get('SERVICE_TYPE', 'web')

# Aguardar serviços dependentes
if service_type != 'rabbitmq_consumer':
# Condicional para verificar PostgreSQL apenas para web e celery (rabbitmq_consumer não precisa).
    db_user = os.environ.get('DB_USER', '')
    db_password = os.environ.get('DB_PASSWORD', '')
    db_host = os.environ.get('DB_HOST', '')
    db_port = os.environ.get('DB_PORT', '')
    db_name = os.environ.get('DB_NAME', '')
    if not all([db_user, db_password, db_host, db_port, db_name]):
        print("Erro: Variáveis DB_USER, DB_PASSWORD, DB_HOST, DB_PORT ou DB_NAME não definidas.")
        sys.exit(1)
    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    if not wait_for_service("PostgreSQL", ['psql', db_url, '-c', '\q']):
        sys.exit(1)

# Aguardar RabbitMQ
if not wait_for_service("RabbitMQ", ['nc', '-z', 'rabbitmq', '5672']):
    sys.exit(1)

# Aguardar MinIO
if not wait_for_service("MinIO", ['curl', '-s', 'http://minio:9000/minio/health/live']):
    sys.exit(1)

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