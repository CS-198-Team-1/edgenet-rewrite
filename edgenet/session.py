import json
from .constants import *


class EdgeNetSession:
    """
    A wrapper for an EdgeNet session.
    """
    def __init__(self, session_id, websocket):
        self.session_id = session_id
        self.websocket  = websocket
        
        self.terminated = False

    @classmethod
    def create_from_handshake(cls, raw_json, websocket):
        json_dict = json.loads(raw_json)
        return cls(json_dict["session_id"], websocket)

    @property
    def status(self):
        if self.terminated: return SESSION_TERMINATED
        return SESSION_CONNECTED if self.websocket.open else SESSION_DISCONNECTED

    def terminate(self):
        self.terminated = True
        self.websocket = None
