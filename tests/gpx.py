import unittest
import datetime
from freezegun import freeze_time
from unittest.mock import patch
from dateutil import parser as dttm_parser
from gpx import parser
from gpx.wrappers import GPXCollection, GPXEntry, GPXException


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
        
        self.dttms = { i: dttm_parser.parse(t).replace(tzinfo=None)
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
        self.assertIsInstance(gpx_collection.entries[0].dttm, datetime.datetime)
    
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

    @freeze_time("2022-02-10T00:00:00Z")
    def test_parse_gpx_and_sync_now(self):
        gpx_collection = parser.parse_gpx_and_sync_now(
            self.gpx_file_path
        )

        # Initialize start time
        mocked_start_time = "2022-02-10T00:00:00Z"

        # Mock datetime object 
        with patch("datetime.datetime") as mocked_dttm:
            mocked_dttm.now.return_value = dttm_parser.parse(mocked_start_time)

        # Generate correct timestamps
        synced_dttms = { i: f"2022-02-10T00:00:0{i}Z" for i in range(10) }
        synced_dttms = { i: dttm_parser.parse(t).replace(tzinfo=None)
            for i, t in synced_dttms.items() }

        # Assert if all dttms are correct:
        for i, dttm in synced_dttms.items():
            entry = gpx_collection.entries[i]
            self.assertEqual(entry.dttm, dttm)

        # Assert if latlngs are still correct:
        for i, latlng in self.latlngs.items():
            entry = gpx_collection.entries[i]
            self.assertEqual(entry.lat, latlng[0])
            self.assertEqual(entry.lng, latlng[1])

    @freeze_time("2022-02-10T00:00:00Z")
    def test_get_latest_entry(self):
        gpx_collection = parser.parse_gpx_and_sync_now(
            self.gpx_file_path
        )

        # We should get the final entry on the GPX by default
        entry = gpx_collection.get_latest_entry()
        expected_time = dttm_parser.parse("2022-02-10T00:00:09Z").replace(tzinfo=None)
        
        self.assertEquals(entry.dttm, expected_time)

    @freeze_time("2022-02-10T00:00:00Z")
    def test_get_latest_entry_exact(self):
        gpx_collection = parser.parse_gpx_and_sync_now(
            self.gpx_file_path
        )
                
        # Test is 00:05, we should get exactly 00:05
        test_time = dttm_parser.parse("2022-02-10T00:00:05Z").replace(tzinfo=None)
        entry = gpx_collection.get_latest_entry(test_time)
        expected_time = dttm_parser.parse("2022-02-10T00:00:05Z").replace(tzinfo=None)
        
        self.assertEquals(entry.dttm, expected_time)

    @freeze_time("2022-02-10T00:00:00Z")
    def test_get_latest_entry_non_exact(self):
        gpx_collection = parser.parse_gpx_and_sync_now(
            self.gpx_file_path
        )
        
        # Test is 00:03.5, we should get 00:03, not 00:04 or anything
        test_time = dttm_parser.parse("2022-02-10T00:00:03.5Z").replace(tzinfo=None)
        entry = gpx_collection.get_latest_entry(test_time)
        expected_time = dttm_parser.parse("2022-02-10T00:00:03Z").replace(tzinfo=None)
        
        self.assertEquals(entry.dttm, expected_time)

    @freeze_time("2022-02-10T00:00:00Z")
    def test_get_latest_entry_does_not_exist(self):
        gpx_collection = parser.parse_gpx_and_sync_now(
            self.gpx_file_path
        )
        
        # Date is too early for any entry
        test_time = dttm_parser.parse("2022-02-09T00:00:05Z").replace(tzinfo=None)
        
        self.assertRaises(
            GPXException, gpx_collection.get_latest_entry, test_time
        )
