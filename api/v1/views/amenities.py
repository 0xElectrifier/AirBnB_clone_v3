#!/usr/bin/python3
"""Defines the Amenity api"""
from api.v1.views import app_views
from flask import abort
from flask import jsonify
from flask import request
from models import storage


@app_views.route('/amenities', strict_slashes=False, methods=["GET"])
@app_views.route('/amenities/<amenity_id>', strict_slashes=False,
                 methods=["GET"])
def fetch_amenity(amenity_id=None):
    """Retrieves a list of Amenity objects if @amenity_id is specified
    or just one object if argument is not none
    """
    if amenity_id is None:
        obj = storage.all("Amenity")
        for key, value in obj.items():
            obj[key] = value.to_dict()
    else:
        obj = storage.get("Amenity", amenity_id)
        if obj is None:
            abort(404)
        obj = obj.to_dict()

    return jsonify(obj)


@app_views.route('/amenities/<amenity_id>', strict_slashes=False,
                 methods=['DELETE'])
def delete_amenity(amenity_id):
    """Deletes an Amenity object from database"""
    key = "Amenity." + amenity_id
    amenities = storage.all("Amenity")
    if key in amenities:
        storage.delete(amenities[key])
    else:
        abort(404)

    storage.save()
    return jsonify({}), 200


@app_views.route('/amenities', strict_slashes=False,
                 methods=["POST"])
def post_amenity():
    """Handles post request to the `Amenity` class"""
    try:
        data = request.get_json()
    except Exception:
        data = None
    if not data:
        return "Not a JSON", 400

    try:
        name = data['name']
    except KeyError:
        return 'Missing name', 400

    from models.amenity import Amenity
    new_obj = Amenity(**data)
    new_obj.save()

    return jsonify(new_obj.to_dict()), 201


@app_views.route('/amenities/<amenity_id>', strict_slashes=False,
                 methods=['PUT'])
def update_amenity(amenity_id):
    """Makes an HTTP PUT request, to update the Amenity objects in database"""
    obj = storage.get("Amenity", amenity_id)
    if obj is None:
        abort(404)

    try:
        data = request.get_json()
    except Exception:
        data = None
    if not data:
        return "Not a JSON", 400

    for key, value in data.items():
        if key in ['id', 'created_at', 'updated_at']:
            continue
        setattr(obj, key, value)

    obj.save()
    return jsonify(obj.to_dict()), 200
