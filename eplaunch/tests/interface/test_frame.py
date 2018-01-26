import unittest


class TestA(unittest.TestCase):

    def test_a(self):
        self.assertEqual('foo'.upper(), 'FOO')
