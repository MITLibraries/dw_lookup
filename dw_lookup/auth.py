from __future__ import absolute_import

from flask import abort, make_response, request
from functools import wraps

import os
import sys

server_token = os.environ.get('DW_LOOKUP_TOKEN')

if (server_token is None or server_token == ''):
    sys.exit('missing DW_LOOKUP_TOKEN in env')


def authenticate(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        client_token = request.headers.get('token') or \
            request.args.get('token')

        if (client_token is None or client_token == ''):
            response = make_response()
            response.status_code = 401
            response.headers = {
                'X-Status-Reason': 'client_token missing from request'
            }
            return abort(response)

        if (server_token != client_token):
            response = make_response()
            response.status_code = 401
            response.headers = {
                'X-Status-Reason': 'client_token must match server_token'
            }
            return abort(response)

        return f(*args, **kwargs)
    return wrapper
