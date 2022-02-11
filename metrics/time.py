import time, uuid


class Timer:
    """
    A class that handles the timing of specific code sections in a given function
    """
    def __init__(self, function_name, call_id=None):
        self.call_id       = call_id or str(uuid.uuid4())
        self.function_name = function_name

        self.function_time = TimerSection()

        # Initialize section containers
        self.sections = {}
        self.looped_sections = {}

    def __repr__(self):
        return f"<Timer sections:{self.sections.keys()}, looped:{self.looped_sections.keys()}>"

    def end_function(self): 
        if self.function_time.end is not None:
            raise TimerException(f"Attempted to mark end of function call twice.")
        self.function_time.end_section()

    def start_section(self, section_id):
        if section_id in self.sections: 
            raise TimerException(f"Attempted to start a section ({section_id}) twice.")
        self.sections[section_id] = TimerSection()

    def end_section(self, section_id):
        if section_id not in self.sections:
            raise TimerException(f"Attempted to end a section ({section_id}) that does not exist.")
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


class TimerException(Exception): pass


def uses_timer(func):

    timer = Timer(func.__name__, str(uuid.uuid4()))

    def wrapper(*args, **kwargs):
        return func(timer, *args, **kwargs)

    return wrapper
