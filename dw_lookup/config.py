import json
import os

import boto3


def configure(app):
    app.config.update(
        AUTHOR_DB_HOST=os.environ.get('AUTHOR_DB_HOST'),
        AUTHOR_DB_PORT=os.environ.get('AUTHOR_DB_PORT'),
        AUTHOR_DB_SID=os.environ.get('AUTHOR_DB_SID'),
        AUTHOR_DB_USER=os.environ.get('AUTHOR_DB_USER'),
        AUTHOR_DB_PASSWORD=os.environ.get('AUTHOR_DB_PASSWORD')
    )
    secret_id = os.environ.get('AWS_SECRET_ID')
    if secret_id:
        client = boto3.client('secretsmanager')
        secret = client.get_secret_value(SecretId=secret_id)
        secret_env = json.loads(secret['SecretString'])
        app.config.update(secret_env)
