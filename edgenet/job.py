
from datetime import datetime
from .constants import *
from .message import EdgeNetMessage


class EdgeNetJob:
    """
    A wrapper for a job that is executed through EdgeNetServer.send_command
    """
    def __init__(self, job_id, function_name, args=[], kwargs={}):
        self.job_id        = job_id
        self.function_name = function_name
        self.args          = args
        self.kwargs        = kwargs

        self.results = []
    
    @property
    def raw_results(self):
        return [r.result for r in self.results]

    def create_command_message(self, target):
        return EdgeNetMessage(
            target, MSG_COMMAND,
            job_id        = self.job_id,
            function_name = self.function_name,
            args          = self.args,
            kwargs        = self.kwargs
        )

    def register_result_from_message(self, message: EdgeNetMessage):
        new_result = EdgeNetJobResult(
            message.session_id,
            message.result,
            message.sent_dttm,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        self.results.append(new_result)


class EdgeNetJobResult:
    """
    A wrapper for a job result
    """
    def __init__(self, session_id, result, sent_dttm, recv_dttm):
        self.session_id = session_id
        self.result     = result
        self.sent_dttm  = sent_dttm
        self.recv_dttm  = recv_dttm
