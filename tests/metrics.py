import unittest
import time
from metrics.time import TimerException, uses_timer


class TestMetrics(unittest.TestCase):
    def test_working_simple(self):
        """
        Tests if simple Timer sections are working correctly.
        """
        @uses_timer
        def sleeper(timer):
            timer.start_section("1")
            time.sleep(0.01)
            timer.end_section("1")
            timer.end_function()
            return timer

        timer = sleeper()
        self.assertGreater(timer.sections["1"].elapsed, 0.0)

    def test_working_looped(self):
        """
        Tests if looped Timer sections are working correctly.
        """
        @uses_timer
        def sleeper(timer):
            for _ in range(5):
                timer.start_looped_section("1")
                time.sleep(0.002)
                timer.end_looped_section("1")
            timer.end_function()
            return timer

        timer = sleeper()
        
        for section in timer.looped_sections["1"]:
            self.assertGreater(section.elapsed, 0.0)

    def test_exception_function_not_ended(self):
        """
        Tests for an exception when a section is never ended.
        """
        @uses_timer
        def sleeper(timer):
            timer.start_section("1")
            timer.end_section("1")
            return timer

        self.assertRaises(TimerException, sleeper)

    def test_exception_section_not_ended(self):
        """
        Tests for an exception when a section is never ended.
        """
        @uses_timer
        def sleeper(timer):
            timer.start_section("1")
            timer.end_function()
            return timer

        self.assertRaises(TimerException, sleeper)

    def test_exception_section_started_twice(self):
        """
        Tests for an exception when a section is started twice.
        """
        @uses_timer
        def sleeper(timer):
            timer.start_section("1")
            timer.start_section("1")
            timer.end_function()
            return timer

        self.assertRaises(TimerException, sleeper)

    def test_exception_section_ended_twice(self):
        """
        Tests for an exception when a section is ended twice.
        """
        @uses_timer
        def sleeper(timer):
            timer.start_section("1")
            timer.end_section("1")
            timer.end_section("1")
            timer.end_function()
            return timer

        self.assertRaises(TimerException, sleeper)

    def test_exception_section_ended_without_starting(self):
        """
        Tests for an exception when a section is ended without being started.
        """
        @uses_timer
        def sleeper(timer):
            timer.end_section("1")
            timer.end_function()
            return timer

        self.assertRaises(TimerException, sleeper)

    def test_exception_section_not_ended_looped(self):
        """
        Tests for an exception when a looped section is never ended.
        """
        @uses_timer
        def sleeper(timer):
            timer.start_looped_section("1")
            timer.end_function()
            return timer

        self.assertRaises(TimerException, sleeper)

    def test_exception_section_started_twice_looped(self):
        """
        Tests for an exception when a looped section is started twice.
        """
        @uses_timer
        def sleeper(timer):
            timer.start_looped_section("1")
            timer.start_looped_section("1")
            timer.end_function()
            return timer

        self.assertRaises(TimerException, sleeper)

    def test_exception_section_ended_twice_looped(self):
        """
        Tests for an exception when a looped section is ended twice.
        """
        @uses_timer
        def sleeper(timer):
            timer.start_looped_section("1")
            timer.end_looped_section("1")
            timer.end_looped_section("1")
            timer.end_function()
            return timer

        self.assertRaises(TimerException, sleeper)

    def test_exception_section_ended_without_starting_looped(self):
        """
        Tests for an exception when a looped section is ended without being started.
        """
        @uses_timer
        def sleeper(timer):
            timer.end_looped_section("1")
            timer.end_function()
            return timer

        self.assertRaises(TimerException, sleeper)
        