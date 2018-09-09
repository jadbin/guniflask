# coding=utf-8

from flask import Blueprint

hello_world_blueprint = Blueprint('hello_world', __name__, url_prefix='/api')


@hello_world_blueprint.route('/hello-world', methods=['GET'])
def hello_world():
    return 'Hello World!'
