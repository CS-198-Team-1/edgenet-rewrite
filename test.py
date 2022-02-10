import unittest
import tests


def suite():
    suite = unittest.TestLoader().loadTestsFromModule(tests.edgenet)
    suite = unittest.TestLoader().loadTestsFromModule(tests.gpx)
    
    return unittest.TestSuite([suite])


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())
