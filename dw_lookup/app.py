from flask import Flask, jsonify, request
from flask_cors import CORS

from dw_lookup.auth import authenticate
from dw_lookup.config import configure
from dw_lookup.dw import db, get_orcid, get_author, search_authors


app = Flask(__name__)
configure(app)
db.configure(app.config['AUTHOR_DB_HOST'], app.config['AUTHOR_DB_PORT'],
             app.config['AUTHOR_DB_SID'], app.config['AUTHOR_DB_USER'],
             app.config['AUTHOR_DB_PASSWORD'])
CORS(app)


@app.route('/orcid/<mit_id>', methods=['GET'])
@authenticate
def orcid(mit_id):
    return jsonify(get_orcid(mit_id))


@app.route('/author/<mit_id>', methods=['GET'])
@authenticate
def author(mit_id):
    return jsonify(get_author(mit_id))


@app.route('/authors', methods=['GET'])
@authenticate
def authors():
    return jsonify(search_authors(first=request.args.get('first'),
                                  last=request.args.get('last')))
