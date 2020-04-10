from ioformats import availableWriters,TABLE
from ioformats.text import TextWriter


class CSVwriter(TextWriter):
    def __init__(self, numbered=False, outputDir='.',multiSheetOutput=False,editMode=False,extension='.csv',sep=';'):
        super().__init__(numbered,outputDir,multiSheetOutput,editMode,extension,TABLE)
        self.sep = sep


availableWriters['csv'] = CSVwriter()
