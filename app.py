import time

import redis
from flask import Flask
from notifications import send_push_message

APP = Flask(__name__)
CACHE = redis.Redis(host="redis", port=6379)


def get_hit_count():
    retries = 5
    while True:
        try:
            return CACHE.incr("hits")
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)


@APP.route("/")
def hello():
    count = get_hit_count()
    return "Hello World from Docker! I have been seen {} times.\n".format(count)


@APP.route("/message/send")
def send_message():
    target = {"device_id": "foo"}
    send_push_message(target["device_id"], "You've got the potato!")


if __name__ == "__main__":
    APP.run(host="0.0.0.0", debug=True)
