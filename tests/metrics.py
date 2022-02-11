import unittest
import time
from metrics.time import TimerException, uses_timer


class TestGPX(unittest.TestCase):
    def test_working_simple(self):
        @uses_timer
        def sleeper(timer):
            timer.start_section("1")
            time.sleep(0.01)
            timer.end_section("1")
            return timer

        timer = sleeper()
        self.assertGreater(timer.sections["1"].elapsed, 0.0)

    def test_working_looped(self):
        @uses_timer
        def sleeper(timer):
            for i in range(5):
                timer.start_looped_section("1")
                time.sleep(0.002)
                timer.end_looped_section("1")
            return timer

        timer = sleeper()
        
        for section in timer.looped_sections["1"]:
            self.assertGreater(section.elapsed, 0.0)

    def test_exception_not_ended(self):
        @uses_timer
        def sleeper(timer):
            timer.start_section("1")
            return timer

        self.assertRaises(TimerException, sleeper)

    def test_exception_started_twice(self):
        @uses_timer
        def sleeper(timer):
            timer.start_section("1")
            timer.start_section("1")
            return timer

        self.assertRaises(TimerException, sleeper)

    def test_exception_ended_twice(self):
        @uses_timer
        def sleeper(timer):
            timer.start_section("1")
            timer.end_section("1")
            timer.end_section("1")
            return timer

        self.assertRaises(TimerException, sleeper)

    def test_exception_ended_without_starting(self):
        @uses_timer
        def sleeper(timer):
            timer.end_section("1")
            return timer

        self.assertRaises(TimerException, sleeper)

    def test_exception_not_ended_looped(self):
        @uses_timer
        def sleeper(timer):
            timer.start_looped_section("1")
            return timer

        self.assertRaises(TimerException, sleeper)

    def test_exception_started_twice_looped(self):
        @uses_timer
        def sleeper(timer):
            timer.start_looped_section("1")
            timer.start_looped_section("1")
            return timer

        self.assertRaises(TimerException, sleeper)

    def test_exception_ended_twice_looped(self):
        @uses_timer
        def sleeper(timer):
            timer.start_looped_section("1")
            timer.end_looped_section("1")
            timer.end_looped_section("1")
            return timer

        self.assertRaises(TimerException, sleeper)

    def test_exception_ended_without_starting_looped(self):
        @uses_timer
        def sleeper(timer):
            timer.end_looped_section("1")
            return timer

        self.assertRaises(TimerException, sleeper)
        