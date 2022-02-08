import unittest
import tests
import unittest


def suite():
    suite = unittest.TestLoader().loadTestsFromModule(tests.edgenet)
    
    return unittest.TestSuite([suite])


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())
