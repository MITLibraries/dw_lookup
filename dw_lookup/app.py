#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from dw_lookup.auth import authenticate
from dw_lookup.dw import DWService
from flask import Flask, jsonify, request
from flask.ext.cors import CORS

def create_app(config_obj=None):
    app = Flask(__name__)

    cors = CORS(app, resources=r'/author/*')
    @app.route('/author/<mit_id>', methods=['GET'])
    @authenticate
    def author(mit_id):
        with DWService() as dw_service:
            return jsonify(dw_service.get_author({'mit_id': mit_id}))

    cors = CORS(app, resources=r'/authors*')
    @app.route('/authors', methods=['GET'])
    @authenticate
    def search_authors():
        with DWService() as dw_service:
            return jsonify(dw_service.search_authors({
                'first':request.args.get('first'),
                'last':request.args.get('last')
            }))

    return app