from .parser import parse_gpx_and_sync_now

def uses_gpx(gpx_file_path):

    def _uses_gpx(func):

        def wrapper(*args, **kwargs):
            # Parse the GPXCollection
            gpx_collection = parse_gpx_and_sync_now(gpx_file_path)

            # Pass the GPXCollection here
            result = func(gpx_collection, *args, **kwargs)
            return result

        return wrapper

    return _uses_gpx