

class GPXCollection:
    """
    A wrapper for a collection of GPX entries
    """
    def __init__(self, filepath, start_time):
        self.filepath   = filepath
        self.start_time = start_time

        # Initialize empty entries list (ordered)
        self.entries    = []

    def __repr__(self): 
        return f"<GPXCollection start:{self.start_time}, entries:{len(self.entries)}>"

    def get_latest_entry(self, dttm=None):
        if dttm is None: return self.entries[-1] # Return latest by default
        if dttm < self.entries[0].dttm: # Throw an error if dttm is earlier than first
            raise GPXException("There is no matching entry since the provided datetime.")
        
        entries_before_dttm = [e for e in self.entries if e.dttm <= dttm]
        
        return entries_before_dttm[-1] # Return the latest of those entries


class GPXEntry:
    """
    A wrapper for a GPX entry
    """
    def __init__(self, dttm, lat, lng, ele=None, speed=None):
        self.dttm   = dttm
        self.latlng = (lat, lng)
        self.ele    = ele
        self.speed  = speed

    def __repr__(self): return f"<GPXEntry [{self.dttm}]: {self.latlng}>"

    @property
    def lat(self): return self.latlng[0]

    @property
    def lng(self): return self.latlng[1]


class GPXException(Exception):
    pass
        