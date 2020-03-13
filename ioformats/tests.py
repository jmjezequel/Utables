import logging
import os
import tempfile
import unittest
from datetime import datetime

from ioformats import *
from ioformats import TABLE
from ioformats.writers import AbstractWriter

TEST_TABLE = [
    ['Test Table', 'String', 'Int', 'Float', 'Date'],
    ['Line 1', 'foo', 42, 3.14, datetime(2000,1,1).date()],
    ['Line 2', '', 6666666, -0.14, datetime(2020, 1, 1).date()],
    ['Line 3', '%èé&à', None, 0, None],
]

outdir = tempfile.gettempdir() + "/TestWriterMethods/"

def gen_sheet(writer: AbstractWriter, label: str, numbered=False, resetCount=True, **kargs):
    writer.openSheet(label,TABLE,numbered,resetCount,**kargs)
    writer.writeTitle(TEST_TABLE[0])
    for i in range(1,len(TEST_TABLE)):
        writer.writeln(TEST_TABLE[i])
    writer.closeSheet()

def gen_simple_table(writer: AbstractWriter, filename: str, sheets: int = 1):
    writer.open(filename)
    for i in range(0,sheets):
        gen_sheet(writer,"Sheet #"+str(i))
    writer.close()

def get_writers(sheetType: str):
    return filter(lambda w: w.isSupporting(sheetType), availableWriters.values())

class TestWriterMethods(unittest.TestCase):
    def setUp(self):
        os.makedirs(outdir, exist_ok=True)

    def tearDown(self):
        pass
    
    def test_table_writers(self):
        for k, w in availableWriters.items():
            print(k,w.getSupportedTypes())
            if w.isSupporting(TABLE):
                w.setOutputDir(outdir)
                print('Writing 3 sheets table with '+k)
                gen_simple_table(w,k,3)
#        self.assertEqual('foo'.upper(), 'FOO')

    # def test_isupper(self):
    #     self.assertTrue('FOO'.isupper())
    #     self.assertFalse('Foo'.isupper())
    #
    # def test_split(self):
    #     s = 'hello world'
    #     self.assertEqual(s.split(), ['hello', 'world'])
    #     # check that s.split fails when the separator is not a string
    #     with self.assertRaises(TypeError):
    #         s.split(2)


if __name__ == '__main__':
    unittest.main()