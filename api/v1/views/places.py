#!/usr/bin/python3
"""Defines the 'Place' api uri"""
from api.v1.views import app_views
from flask import abort, jsonify, request
from models import storage


@app_views.route('/cities/<city_id>/places', strict_slashes=False)
def fetch_city_places(city_id):
    """Returns the list of all `Place` objects of a `City`"""
    city = storage.get("City", city_id)
    if city is None:
        abort(404)

    return jsonify([place.to_dict() for place in city.places])


@app_views.route('/places/<place_id>', strict_slashes=False)
def fetch_places_2(place_id):
    """Retrieves a `Place` object"""
    place = storage.get("Place", place_id)
    if place is None:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route('/places/<places_id>', strict_slashes=False,
                 methods=["DELETE"])
def delete_place(places_id):
    """Deletes a place object with an id == @places_id"""
    place = storage.get("Place", places_id)
    if place is None:
        abort(404)
    else:
        storage.delete(place)

    storage.save()
    return jsonify({}), 200


@app_views.route('/cities/<city_id>/places', strict_slashes=False,
                 methods=["POST"])
def post_place(city_id):
    """Handles post request to the `Place` uri"""
    city = storage.get("City", city_id)
    if city is None:
        abort(404)

    data = request.get_json()
    if not data:
        return "Not a JSON", 400

    user_id = data.get('user_id')
    if user_id is None:
        return "Missing user_id", 400
    if storage.get("User", user_id) is None:
        abort(404)
    if data.get('name') is None:
        return "Missing name"

    from models.place import Place
    new_place = Place(**data)
    # Make sure 'city_id' wasn't omitted in data
    setattr(new_place, 'city_id', city_id)
    new_place.save()

    return jsonify(new_place.to_dict()), 201


@app_views.route('/places/<place_id>', strict_slashes=False,
                 methods=["PUT"])
def update_places(place_id):
    """Updates a `Place` object"""
    place = storage.get("Place", place_id)
    if place is None:
        abort(404)

    data = request.get_json()
    if not data:
        return "Not a JSON", 400

    for key, value in data.items():
        if key in ['id', 'user_id', 'city_id', 'created_at', 'updated_at']:
            continue
        setattr(place, key, value)

    place.save()
    return jsonify(place.to_dict()), 200
