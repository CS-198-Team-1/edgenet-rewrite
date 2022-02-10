import unittest
from dateutil import parser as dttm_parser
from datetime import datetime
from gpx import parser
from gpx.wrappers import GPXCollection, GPXEntry


class TestGPX(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()

        # Initialize GPX file details:
        self.gpx_file_path = "experiment-files/test.gpx"
        
        dttms = {
            0: "2020-09-24T04:09:25Z",
            1: "2020-09-24T04:09:26Z",
            9: "2020-09-24T04:09:34Z",
        }
        
        self.dttms = { i: dttm_parser.parse(t)
            for i, t in dttms.items() }

        self.latlngs = {
            0: (14.6490481666667, 121.068924666667),
            4: (14.649171, 121.068884666667),
            9: (14.6495368333333, 121.068730833333)
        }
    
    def test_parse_gpx_init(self):
        gpx_collection = parser.parse_gpx(
            self.gpx_file_path
        )

        self.assertIsInstance(gpx_collection, GPXCollection)
        self.assertIsInstance(gpx_collection.entries[0], GPXEntry)
        self.assertIsInstance(gpx_collection.entries[0].dttm, datetime)
    
    def test_parse_gpx_correctness(self):
        gpx_collection = parser.parse_gpx(
            self.gpx_file_path
        )

        # Assert if there are actually 10 entries
        self.assertEqual(len(gpx_collection.entries), 10)
        
        # Assert if datetimes are correct:
        for i, dttm in self.dttms.items():
            entry = gpx_collection.entries[i]
            self.assertEqual(entry.dttm, dttm)

        # Assert if latlngs are correct:
        for i, latlng in self.latlngs.items():
            entry = gpx_collection.entries[i]
            self.assertEqual(entry.lat, latlng[0])
            self.assertEqual(entry.lng, latlng[1])
