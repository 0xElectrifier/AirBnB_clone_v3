#!/usr/bin/python3
"""states routes module"""
from api.v1.views import app_views
from api.v1.views import *
from models import storage
from flask import jsonify, make_response, abort, request
from models.state import State


@app_views.route('/states', strict_slashes=False, methods=['GET'])
@app_views.route('/states/<state_id>', strict_slashes=False, methods=['GET'])
def states(state_id=None):
    """[GET] Retrieves a list of all State objects"""
    if not state_id:
        objs = [obj.to_dict() for obj in storage.all('State').values()]
    else:
        objs = storage.get("State", state_id)
        if objs is None:
            abort(404)
        obj = obj.to_dict()
    return jsonify(objs)


@app_views.route('/states/<state_id>', strict_slashes=False,
                 methods=['DELETE'])
def del_state(state_id):
    """[DELETE] - deletes a state object with specified id"""

    key = "State." + state_id
    states = storage.all("State")
    if key in states:
        storage.delete(states[key])
    else:
        abort(404)

    storage.save()
    return jsonify({}), 200


@app_views.route('/states', strict_slashes=False, methods=['POST'])
def create_state():
    """[POST] - adds a state object"""

    data = request.get_json()
    if not data:
        return "Not a JSON", 400

    try:
        name = data['name']
    except KeyError:
        return 'Missing name', 400

    from models.state import State
    new_obj = State(**data)
    new_obj.save()

    return jsonify(new_obj.to_dict()), 201


@app_views.route('/states/<state_id>', strict_slashes=False, methods=['PUT'])
def update_state(state_id):
    """[PUT] - updates a state object"""
    obj = storage.get("State", state_id)
    if obj is None:
        abort(404)

    data = request.get_json()
    if not data:
        return "Not a JSON", 400

    for key, value in data.items():
        if key in ['id', 'created_at', 'updated_at']:
            continue
        setattr(obj, key, value)

    obj.save()
    return jsonify(obj.to_dict()), 200
