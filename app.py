# Mostly just copied from
# https://medium.com/google-cloud/firebase-developing-a-web-service-with-admin-sdk-flask-and-google-cloud-6fb97eb38b80
import random
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, abort
import firebase_admin
from firebase_admin import db

from notifications import send_push_message

APP = Flask(__name__)
firebase_admin.initialize_app(
    options={"databaseURL": "https://hot-potato-11fd8.firebaseio.com/"}
)
USERS = db.reference("users")
POTATO = db.reference("potato")


@APP.route("/")
def hello():
    count = 222222222222222
    return "Hello World from Docker! I have been seen {} times.\n".format(count)


@APP.route("/message/send")
def send_message():
    target = {"device_id": "foo"}
    send_push_message(target["device_id"], "You've got the potato!")


@APP.route("/register", methods=["POST"])
def register_user():
    req = request.get_json(force=True)
    user = USERS.push(req)
    return jsonify({"id": user.key}), 201


@APP.route("/random")
def get_random_user():
    user = _get_random_user()
    return jsonify(user)


@APP.route("/potato", methods=["POST"])
def handle_potato():
    potato, potato_id = _get_first_potato()
    if potato_id:
        potato = _new_holder(potato)
        POTATO.child(potato_id).update(potato)
    else:
        POTATO.push(potato)
    return jsonify(potato)


@APP.route("/potato", methods=["GET"])
def get_potato():
    potato = _get_first_potato()
    return jsonify(potato)


def _ensure_potato(potato_id):
    potato = POTATO.child(potato_id).get()
    if not potato:
        abort(404)
    return potato


def _get_first_potato():
    potato = POTATO.order_by_key().limit_to_first(1).get()
    if not potato:
        return (_create_potato(), None)
    potato_id = list(potato.keys())[0]
    peeled_potato = potato[potato_id]
    return peeled_potato, potato_id


def _create_potato():
    catcher = _get_random_user()
    potato = {
        "explosion": _get_random_explosion_time(),
        "holder": {"id": catcher["user_id"], "username": catcher["username"]},
    }
    return potato


def _get_random_user(exclude_user_id=None):
    users = USERS.get()
    user_ids = list(users)
    if exclude_user_id:
        user_ids.remove(exclude_user_id)
    random_user_id = random.choice(user_ids)
    user = users[random_user_id]
    user["user_id"] = random_user_id
    return user


def _new_holder(potato):
    if "holder" in potato:
        catcher = _get_random_user(potato["holder"]["id"])
    else:
        catcher = _get_random_user()
    potato["holder"] = {"id": catcher["user_id"], "username": catcher["username"]}
    return potato


def _get_random_explosion_time():
    now = datetime.now()
    time_to_explosion = random.randrange(5, 10)
    explosion_time_timestamp = (now + timedelta(seconds=time_to_explosion)).isoformat()
    return explosion_time_timestamp


if __name__ == "__main__":
    APP.run(host="0.0.0.0", debug=True)
