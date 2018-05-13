# Mostly just copied from
# https://medium.com/google-cloud/firebase-developing-a-web-service-with-admin-sdk-flask-and-google-cloud-6fb97eb38b80
import random
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
    potato = {"foo": "bar"}
    potato = POTATO.push(potato)

    return jsonify(potato)


@APP.route("/potato/<potato_id>")
def get_potato(potato_id):
    potato = _ensure_potato(potato_id)
    return jsonify(potato)


def _ensure_potato(potato_id):
    potato = POTATO.child(potato_id).get()
    if not potato:
        abort(404)
    return potato


def _get_random_user():
    users = USERS.get()
    random_user_id = random.choice(list(users))
    user = users[random_user_id]
    return user


if __name__ == "__main__":
    APP.run(host="0.0.0.0", debug=True)
