import unittest

from models.marks import add_marks_batch


class TestMarksBatch(unittest.TestCase):
    def test_add_marks_batch_requires_entries(self):
        with self.assertRaises(Exception):
            add_marks_batch(1, [])


if __name__ == "__main__":
    unittest.main()
