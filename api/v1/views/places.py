#!/usr/bin/python3
"""Defines the 'Place' api uri"""
from api.v1.views import app_views
from flask import abort, jsonify, request
from models import storage
from os import getenv
import requests


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
        return "Missing name", 400

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


@app_views.route('/places_search', strict_slashes=False,
                 methods=["POST"])
def search_places():
    """Retrieves all 'Place' objects depending of the JSON
    in the body of the request
    """
    data = request.get_json()
    if data is None:
        return "Not a JSON", 400

    classes = ["amenities", "cities", "states"]
    result_places = []
    HBNB_API_PORT = getenv('HBNB_API_PORT')
    if HBNB_API_PORT is None:
        HBNB_API_PORT = '5050'

    root_url = 'http://0.0.0.0:{}/api/v1'.format(HBNB_API_PORT)

    for key, id_list in data.items():
        if key not in classes:
            continue
        if key == "states":
            for state_id in id_list:
                s_cities_url = root_url + '/states/{}/cities'
                s_cities = requests.get(s_cities_url.format(state_id))
                if s_cities.status_code > 299:
                    continue
                s_cities = s_cities.json()
                for sc_id in s_cities:
                    c_places_url = root_url + '/cities/{}/places'
                    c_places = requests.get(c_places_url.format(sc_id))
                    if c_places.status_code > 299:
                        continue
                    result_places.append(place for place in c_places)
        elif key == "cities":
            for city_id in id_list:
                curr_city_url = root_url + '/cities/{}'.format(city_id)
                current_city = requests.get(curr_city_url)
                if current_city.status_code > 299:
                    continue

                current_city = current_city.json()
                if (('states' in data) and
                   (current_city.state_id in data['states'])):
                    continue

                c_places_url = root_url + '/cities/{}/places'
                c_places_2 = requests.get(c_places_url.format(city_id))
                c_places_2 = c_places_2.json()
                result_places.append(place for place in c_places_2)

    # If at this point 'result_places' is empty, fetch all 'Place' objects
    if len(result_places) == 0:
        all_place = storage.all('Place')
        for key, value in all_place.items():
            all_place[key] = value.to_dict()
            result_places.append(all_place[key])

    if 'amenities' in data:
        amenities_id = data['amenities']
        for place in result_places:
            p_obj = storage.get('Place', place['id'])
            p_amenities_id = p_obj.amenity_ids

            for a_id in amenities_id:
                if a_id not in p_amenities_id:
                    result_places.remove(place)

    return jsonify(result_places), 200
