#!/usr/bin/python3
"""Defines `User` api"""
from api.v1.views import app_views
from flask import abort, jsonify, request
from models import storage


@app_views.route("/users", strict_slashes=False, methods=["GET"])
@app_views.route("/users/<user_id>", strict_slashes=False, methods=["GET"])
def fetch_users(user_id=None):
    """Fetches a `User` object with 'id' == @user_id if @user_id is not None,
    otherwise fetches all objects
    """
    if user_id is None:
        obj = storage.all("User").values()
        obj = [user.to_dict() for user in obj]
    else:
        obj = storage.get("User", user_id)
        if obj is None:
            abort(404)
        obj = obj.to_dict()

    return jsonify(obj)


@app_views.route('/users/<user_id>', strict_slashes=False,
                 methods=['DELETE'])
def delete_user(user_id):
    """Deletes a `User` object from database"""
    user = storage.get("User", user_id)
    if user is None:
        abort(404)
    else:
        storage.delete(user)

    storage.save()
    return jsonify({}), 200


@app_views.route('/users', strict_slashes=False,
                 methods=["POST"])
def post_user():
    """Handles post request to the `User` class"""
    data = request.get_json()
    if not data:
        return "Not a JSON", 400

    email = data.get("email")
    if email is None:
        return 'Missing email', 400
    password = data.get("password")
    if password is None:
        return "Missing password", 400

    from models.user import User
    new_user = User(**data)
    new_user.save()

    return jsonify(new_user.to_dict()), 201


@app_views.route('/users/<user_id>', strict_slashes=False,
                 methods=['PUT'])
def update_user(user_id):
    """Makes an HTTP PUT request to update a `User` object in database,
    with @user_id
    """
    user = storage.get("User", user_id)
    if user is None:
        abort(404)

    data = request.get_json()
    if not data:
        return "Not a JSON", 400

    for key, value in data.items():
        if key in ['id', 'email', 'created_at', 'updated_at']:
            continue
        setattr(user, key, value)

    user.save()
    return jsonify(user.to_dict()), 200
