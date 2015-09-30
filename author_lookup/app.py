#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from flask import Flask, jsonify, render_template, request
from flask.ext.cors import CORS
from author_lookup.dw import DWService

def create_app(config_obj=None):
    app = Flask(__name__)

    @app.route('/demo/', methods=['GET'])
    def demo():
        return render_template('demo.html')

    cors = CORS(app, resources=r'/author/*')
    @app.route('/author/', methods=['GET'])
    def author():
        with DWService() as dw_service:
            return jsonify(dw_service.get_data(request.args.get('name_string')))

    return app
