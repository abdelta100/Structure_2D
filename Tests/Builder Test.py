import unittest
import pytest

# TODO get familiar with pytest and write tests to check if code has broken when imporving later

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
