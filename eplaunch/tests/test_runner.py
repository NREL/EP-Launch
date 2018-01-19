import unittest


class TestB(unittest.TestCase):

    def test_b(self):
        self.assertEqual('foo'.upper(), 'FOO')
