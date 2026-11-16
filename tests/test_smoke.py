import unittest
from app import app


class SmokeTest(unittest.TestCase):
    def test_app_exists(self):
        self.assertIsNotNone(app)


if __name__ == "__main__":
    unittest.main()