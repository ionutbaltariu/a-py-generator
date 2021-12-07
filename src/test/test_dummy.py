import unittest


class TestDummy(unittest.TestCase):

    def test_sum(self):
        self.assertEqual(sum([1, 2, 2]), 6, "Should be 6")


if __name__ == '__main__':
    unittest.main()
