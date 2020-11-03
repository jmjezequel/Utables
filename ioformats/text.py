from os import close
from typing import Iterable

from ioformats.filerw import FileWriter
from ioformats import availableWriters, TEXT, TABLE, BIBLIOGRAPHY, LIST


class TextWriter(FileWriter):
    def __init__(self, numbered=False, outputDir='.', multiSheetOutput=False, editMode=False, extension='.txt', *supported: str):
        super().__init__(numbered, outputDir, multiSheetOutput, editMode, extension, * supported)
        self.sep = ' '

    def quote(self, s):
        return str(s)

    def join(self, iterable):
        """ join an iterable of any type to produce a String."""
        return self.sep.join(self.quote(x) for x in iterable)

    def _getopendoc(self):
        if self.multiSheetOutput:
            return open(self.getFilename(), 'w', encoding='utf-8')
        return None

    def openSheet(self, sheetname, sheetType=TEXT, *args, **kwargs):
        super().openSheet(sheetname, sheetType)
        if not self.multiSheetOutput:
            self.doc = open(self.getSheetFilename(), 'w', encoding='utf-8')

    def _savedoc(self, filename):
        self.doc.close()

    def writeRaw(self, *args: str, end='', **kwargs):
        print(*(arg for arg in args), file=self.doc, sep='', end=end)

    def writeEncode(self, arg: Iterable, **kwargs): #arg: Union[str,iterable]
        if isinstance(arg,str):
            self.writeRaw(self.quote(arg), **kwargs)
        else:
            self.writeRaw(self.join(arg), **kwargs)

    def writeTitle(self, arg, **kwargs):
        self.writeEncode(arg, **kwargs)
        super().writeTitle(arg, **kwargs)

    def startNewLine(self):
        self.writeRaw('\n')

    def append(self, element, **kwargs):
        self.writeEncode(element, **kwargs)

    def writeln(self, iterable, **kwargs):
        self.writeEncode(iterable, **kwargs)
        super().writeln(iterable, **kwargs)


availableWriters['txt'] = TextWriter()
availableWriters['txt-multisheets'] = TextWriter(multiSheetOutput=True)
