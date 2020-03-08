import unittest
from datetime import datetime

TABLE = [
    ['Test Table', 'String', 'Int', 'Float', 'Date'],
    ['Line 1', 'foo', 42, 3.14, datetime(2000,1,1)],
    ['Line 2', 'bar', 6666666, 0.14, datetime(2020, 1, 1)],
    ['Line 3', '%èé&à', None, 0, None],
]

class TestWriterMethods(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)


if __name__ == '__main__':
    unittest.main()