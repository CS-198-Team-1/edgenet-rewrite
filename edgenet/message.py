import json
from constants import *


class EdgeNetMessage:
    """
    A wrapper for an EdgeNet message.
    """
    def __init__(self, session_id, msg_type):
        self.session_id = session_id
        self.msg_type   = msg_type

    @classmethod
    def create_from_json(cls, raw_json):
        json_dict = json.loads(raw_json)
        return cls(
            json_dict["session_id"],
            json_dict["msg_type"]
        )

    @classmethod
    def create_client_handshake_message(cls, session_id):
        return cls(session_id, MSG_CONNECTION)