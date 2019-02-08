from functools import wraps

from flask import abort, request, current_app
from werkzeug.security import safe_str_cmp


def authenticate(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        apikey = current_app.config['DW_LOOKUP_TOKEN']
        if not apikey:
            raise Exception("Server API key not set")

        client_token = request.headers.get('token') or \
            request.args.get('token', "")

        if safe_str_cmp(apikey, client_token):
            return f(*args, **kwargs)

        abort(401)
    return wrapper
