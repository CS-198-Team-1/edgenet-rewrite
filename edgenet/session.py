import json
from edgenet.constants import *


class EdgeNetSession:
    """
    A wrapper for an EdgeNet session.
    """
    def __init__(self, session_id, websocket, status=SESSION_CONNECTED):
        self.session_id = session_id
        self.websocket  = websocket
        self.status     = status

    @classmethod
    def create_from_handshake(cls, raw_json, websocket):
        json_dict = json.loads(raw_json)
        return cls(
            json_dict["session_id"],
            websocket,
            SESSION_CONNECTED # We assume it's connected, it's from a handshake
        )
