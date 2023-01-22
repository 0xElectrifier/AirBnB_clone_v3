#!/usr/bin/python3
"""Defines the Amenity api"""
from api.v1.views import app_views
from flask import abort
from flask import request
from models import storage


@app_views.route('/amenities', methods=["GET"])
@app_views.route('/amenities/<amenity_id>', methods=["GET"])
def fetch_amenity(amenity_id=None):
    """Retrieves a list of Amenity objects if @amenity_id is specified
    or just one object if argument is not none
    """
    if amenity_id == None:
        obj = storage.all("Amenity")
        for key, value in obj.items():
            obj[key] = value.to_dict()
    else:
        obj = storage.get("Amenity", amenity_id)
        if obj == None:
            abort(404)
        obj = obj.to_dict()


    return obj


@app_views.route('/amenities/<amenity_id>', methods=['DELETE'])
def delete_amenity(amenity_id):
    """Deletes an Amenity object from database"""
    key = "Amenity." + amenity_id
    amenities = storage.all("Amenity")
    if key in amenities:
        storage.delete(amenities[key])
    else:
        abort(404)


@app_views.route('/amenities', methods=["POST"])
def post_amenity():
    """Handles post request to the `Amenity` class"""
    data = request.get_json()
    if not data:
        abort(400, description="Not a JSON")

    try:
        name = data['name']
    except KeyError:
        abort(400, description='Missing name')

    from models.amenity import Amenity
    new_obj = Amenity(**data)
    new_obj.save()


@app_views.route('/amenities/<amenity_id>', methods=['PUT'])
def update_amenity(amenity_id):
    """Makes an HTTP PUT request, to update the Amenity objects in database"""
    obj = storage.get("Amenity", amenity_id)
    if obj is None:
        abort(404)

    data = request.get_json()
    if not data:
        abort(400, description="Not a JSON")
    for key, value in data.items():
        if key in ['id', 'created_at', 'updated_at']:
            continue
        setattr(obj, key, value)

    return obj, 200
