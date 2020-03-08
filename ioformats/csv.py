# import csv
from os import close

from ioformats.filerw import FileWriter
from ioformats import availableWriters,TABLE

class CSVwriter(FileWriter):
    def __init__(self, numbered=False, outputDir='.',multiSheetOutput=False,editMode=False,extension='.csv',sep=';'):
        super().__init__(numbered,outputDir,multiSheetOutput,editMode,extension,TABLE)
        self.sep = sep


availableWriters['csv'] = CSVwriter()
