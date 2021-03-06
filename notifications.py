from exponent_server_sdk import DeviceNotRegisteredError
from exponent_server_sdk import PushClient
from exponent_server_sdk import PushMessage
from exponent_server_sdk import PushResponseError
from exponent_server_sdk import PushServerError
from requests.exceptions import ConnectionError
from requests.exceptions import HTTPError


# Basic arguments. You should extend this function with the push features you
# want to use, or simply pass in a `PushMessage` object.
def send_push_message(token, message, extra=None):
    try:
        response = PushClient().publish(PushMessage(to=token, body=message, data=extra))
    except PushServerError as exc:
        # Encountered some likely formatting/validation error.
        print("pushservererror", exc)
        raise
    except (ConnectionError, HTTPError) as exc:
        # Encountered some Connection or HTTP error - retry a few times in
        # case it is transient.
        print("connection error ", exc)
        raise

    try:
        # We got a response back, but we don't know whether it's an error yet.
        # This call raises errors so we can handle them with normal exception
        # flows.
        response.validate_response()
    except PushResponseError as exc:
        # Encountered some other per-notification error.
        print("pushresponse failed > ", exc)
        raise
