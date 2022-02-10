import unittest
import tests


def suite():
    _edgenet = unittest.TestLoader().loadTestsFromModule(tests.edgenet)
    _gpx = unittest.TestLoader().loadTestsFromModule(tests.gpx)
    
    return unittest.TestSuite([
        _edgenet, _gpx
    ])


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())
