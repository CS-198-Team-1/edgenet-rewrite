import time, uuid, datetime
from dateutil.parser import parse as dttm_parse
from config import *


class Timer:
    """
    A class that handles the timing of specific code sections in a given function
    """
    def __init__(self, function_name, call_id=None):
        self.call_id       = call_id or str(uuid.uuid4())
        self.function_name = function_name

        self.function_time = TimerSection()
        self.function_started = datetime.datetime.now()
        self.function_ended = None

        # Initialize section containers
        self.sections = {}
        self.looped_sections = {}

    def __repr__(self):
        return f"<Timer sections:{self.sections.keys()}, looped:{self.looped_sections.keys()}>"

    def end_function(self):
        for section_id, section in self.sections.items():
            if section.end is None:
                raise TimerException(f"Started section [{section_id}] never ended!")
        for section_id, section_list in self.looped_sections.items():
            for section in section_list:
                if section.end is None:
                    raise TimerException(f"Started looped section [{section_id}] never ended!")
        if self.function_time.end is not None:
            raise TimerException(f"Attempted to mark end of function call twice.")
        
        self.function_time.end_section()
        self.function_ended = datetime.datetime.now()

    def start_section(self, section_id):
        if section_id in self.sections: 
            raise TimerException(f"Attempted to start a section ({section_id}) twice.")
        self.sections[section_id] = TimerSection()

    def end_section(self, section_id):
        if section_id not in self.sections:
            raise TimerException(f"Attempted to end a section ({section_id}) that does not exist.")
        if self.sections[section_id].end is not None:
            raise TimerException(f"Attempted to end a section ({section_id}) twice!")
        self.sections[section_id].end_section()

    def start_looped_section(self, section_id):
        if section_id in self.looped_sections: 
            self.looped_sections[section_id].append(TimerSection())
        else:
            self.looped_sections[section_id] = [TimerSection()]

    def end_looped_section(self, section_id):
        if section_id not in self.looped_sections:
            raise TimerException(f"Attempted to end a looped section ({section_id}) that does not exist.")

        last_section = self.looped_sections[section_id][-1] # Get last section of list

        if last_section.end is not None:
            raise TimerException(f"Attempted to end a looped section ({section_id}) twice.")

        last_section.end_section()

    def to_dict(self):
        json_dict                 = self.__dict__.copy()
        json_dict_sections        = {}
        json_dict_looped_sections = {}

        for section, section_obj in self.sections.items():
            json_dict_sections[section] = section_obj.to_dict()

        for section, section_list in self.looped_sections.items():
            json_dict_looped_sections[section] = [
                s.to_dict() for s in section_list
            ]

        json_dict["sections"]         = json_dict_sections
        json_dict["looped_sections"]  = json_dict_looped_sections
        json_dict["function_time"]    = self.function_time.to_dict()
        json_dict["function_started"] = self.function_started.isoformat()
        json_dict["function_ended"]   = self.function_ended.isoformat()

        return json_dict

    @classmethod
    def create_from_dict(cls, raw_dict):
        timer = cls(
            raw_dict["function_name"], raw_dict["call_id"]
        )
        timer.function_time = TimerSection.create_from_dict(raw_dict["function_time"])
        timer.sections = {
            section: TimerSection.create_from_dict(section_dict) 
            for section, section_dict in raw_dict["sections"].items()
        }
        timer.looped_sections = {
            section: [
                TimerSection.create_from_dict(section_dict)
                for section_dict in section_list
            ] 
            for section, section_list in raw_dict["looped_sections"].items()
        }
        timer.function_started = dttm_parse(raw_dict["function_started"])
        timer.function_ended   = dttm_parse(raw_dict["function_ended"])
        return timer


class TimerSection:
    """
    A wrapper for a timed section of a code block
    """
    def __init__(self):
        self.start = time.perf_counter()
        self.end   = None

    def end_section(self): self.end = time.perf_counter()

    @property
    def elapsed(self):
        if self.end is None: 
            raise TimerException("Attempted to get elapsed of a non-finished section.")
        return self.end - self.start

    def to_dict(self): return self.__dict__

    @classmethod
    def create_from_dict(cls, raw_dict):
        section = cls()
        section.start = raw_dict["start"]
        section.end   = raw_dict["end"]
        return section


class TimerException(Exception): pass


def uses_timer(func):

    def wrapper(*args, **kwargs):
        timer = Timer(func.__name__, str(uuid.uuid4()))

        logging.info(f"Timer metrics instantiated with call ID {timer.call_id}")

        result = func(timer, *args, **kwargs)

        if timer.function_time.end is None:
            raise TimerException("Timer's end_function never called!")

        return result


    return wrapper
