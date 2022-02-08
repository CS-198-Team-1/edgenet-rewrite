import json
from datetime import datetime
from time import strftime
from .constants import *


class EdgeNetMessage:
    """
    A wrapper for an EdgeNet message.
    """
    def __init__(self, session_id, msg_type, **kwargs):
        self.session_id = session_id
        self.msg_type   = msg_type
        
        # From kwargs:
        self.extras = kwargs.keys()
        for k, v, in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def create_from_json(cls, raw_json):
        json_dict = json.loads(raw_json)
        return cls(**json_dict)

    @classmethod
    def create_client_handshake_message(cls, session_id):
        return cls(session_id, MSG_CONNECTION)

    @classmethod
    def create_result_message(cls, session_id, job_id, result):
        return cls(
            session_id, MSG_RESULT,
            job_id=job_id,
            result=result,
            sent_dttm=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )