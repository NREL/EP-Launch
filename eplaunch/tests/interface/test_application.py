import unittest


class TestC(unittest.TestCase):

    def test_c(self):
        self.assertEqual('foo'.upper(), 'FOO')
