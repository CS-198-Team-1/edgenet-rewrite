import asyncio, time
from datetime import datetime
from .constants import *
from .message import EdgeNetMessage


class EdgeNetJob:
    """
    A wrapper for a job that is executed through EdgeNetServer.send_command
    """
    def __init__(self, job_id, function_name, args=[], kwargs={}, callback=None):
        self.job_id        = job_id
        self.function_name = function_name
        self.args          = args
        self.kwargs        = kwargs
        self.callback      = callback

        self.results = []
        self.metrics = {} # Timer object here later

        # Spin lock for finishing a job
        self.finished = False

        # Some validation:
        if not callable(callback) and callback is not None:
            raise EdgeNetJobException("Provided callback is not callable.")
    
    @property
    def raw_results(self):
        return [r.result for r in self.results]

    @property
    def job_started(self):
        return min([ m.function_started for _, m in self.metrics.items() ])

    @property
    def job_ended(self):
        return max([ m.function_ended for _, m in self.metrics.items() ])

    @property
    def elapsed(self):
        return self.job_ended - self.job_started

    def create_command_message(self, target, is_polling):
        return EdgeNetMessage(
            target, MSG_COMMAND_POLL if is_polling else MSG_COMMAND,
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
            datetime.now().isoformat()
        )

        # Append to own results list 
        self.results.append(new_result)

        # If callback exists:
        if self.callback:
            self.callback(new_result)

    def register_metrics(self, timer_obj): self.metrics[timer_obj.call_id] = timer_obj

    def finish_job(self):
        self.finished = True

    def wait_until_finished(self):
        while not self.finished: time.sleep(0.01) # TODO: Improve this spin lock

    def wait_for_metrics(self, number_of_metrics=1):
        while len(self.metrics) != number_of_metrics: time.sleep(0.01) # TODO: Improve this spin lock


class EdgeNetJobResult:
    """
    A wrapper for a job result
    """
    def __init__(self, session_id, result, sent_dttm, recv_dttm):
        self.session_id = session_id
        self.result     = result
        self.sent_dttm  = sent_dttm
        self.recv_dttm  = recv_dttm

    @property
    def args(self): return self.result["args"]

    @property
    def kwargs(self): return self.result["kwargs"]


class EdgeNetJobException(Exception):
    pass