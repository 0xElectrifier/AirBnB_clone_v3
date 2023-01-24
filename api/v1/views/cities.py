#!/usr/bin/python3
"""cities routes module"""
from api.v1.views import app_views
from api.v1.views import *
from flask import jsonify, make_response, abort, request
from models import storage

model = "City"
parent_model = "State"


@app_views.route("/states/<state_id>/cities", strict_slashes=False,
                 methods=["GET"])
def retrieve_cities(state_id):
    """[GET] Retrieves a list of all City objects linked to a state"""
    state = storage.get("State", state_id)
    if state is None:
        abort(404)
    all_cities = [city.to_json() for city in state.cities]
    return jsonify(all_cities)


@app_views.route("/cities/<city_id>", strict_slashes=False, methods=["GET"])
def retrieve_city(city_id):
    """[GET] Retrieves a list of all City objects"""
    city = storage.get("City", city_id)
    if city is None:
        abort(404)
    return jsonify(city.to_json())


@app_views.route("/cities/<city_id>", strict_slashes=False, methods=["DELETE"])
def del_city(city_id):
    """[DELETE] - deletes a city object with specified id"""
    city = storage.get("City", city_id)
    if city is None:
        abort(404)
    storage.delete(city)
    return jsonify({})


@app_views.route("/states/<state_id>/cities", strict_slashes=False,
                 methods=["POST"])
def create_city(state_id):
    """[POST] - adds a city object"""
    try:
        r = request.get_json()
    except:
        r = None
    if r is None:
        return "Not a JSON", 400
    if 'name' not in r.keys():
        return "Missing name", 400
    s = storage.get("State", state_id)
    if s is None:
        abort(404)
    # creates the dictionary r as kwargs to create a city object
    c = City(**r)
    c.state_id = state_id
    c.save()
    return jsonify(c.to_json()), 201


@app_views.route("/cities/<city_id>", methods=["PUT"])
def update_city(city_id):
    """[PUT] - updates a city object"""
    city = storage.get("City", city_id)
    if city is None:
        abort(404)
    try:
        r = request.get_json()
    except:
        r = None
    if r is None:
        return "Not a JSON", 400
    for k in ("id", "created_at", "updated_at", "state_id"):
        r.pop(k, None)
    for k, v in r.items():
        setattr(city, k, v)
    city.save()
    return jsonify(city.to_json()), 200
