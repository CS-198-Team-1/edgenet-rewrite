import datetime
import gpxpy
from .wrappers import GPXCollection, GPXEntry


def parse_gpx_and_sync_now(gpx_file_path):
    gpx_collection = parse_gpx(gpx_file_path)
    
    # Get first entry and get its offset to current time
    first_entry = gpx_collection.entries[0]
    time_now = datetime.datetime.now()
    delta = (time_now - first_entry.dttm)

    for entry in gpx_collection.entries:
        entry.dttm += delta

    gpx_collection.start_time = time_now

    return gpx_collection


def parse_gpx_and_sync(gpx_file_path, base_time):
    gpx_collection = parse_gpx(gpx_file_path)
    
    # Get first entry and get its offset to current time
    first_entry = gpx_collection.entries[0]
    delta = (base_time - first_entry.dttm)

    for entry in gpx_collection.entries:
        entry.dttm += delta

    gpx_collection.start_time = base_time

    return gpx_collection


def parse_gpx(gpx_file_path):
    # Get GPX file
    gpx_file = open(gpx_file_path, 'r')
    gpx_file_obj = gpxpy.parse(gpx_file)

    # Get first time logged
    start_time = gpx_file_obj.tracks[0].segments[0].points[0].time
    
    # Initialize returning object
    gpx_collection = GPXCollection(gpx_file_path, start_time)

    # Loop over each record in each segment in the first track:
    for segment in gpx_file_obj.tracks[0].segments:
        for point in segment.points:
            new_entry = GPXEntry(
                point.time.replace(tzinfo=None), 
                point.latitude, point.longitude,
                ele=point.elevation, speed=point.speed
            )
            gpx_collection.entries.append(new_entry)

    return gpx_collection