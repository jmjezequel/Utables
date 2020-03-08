from os import close
from typing import Iterable

from ioformats.filerw import FileWriter
from ioformats import availableWriters, TEXT, TABLE, BIBLIOGRAPHY, LIST


class TextWriter(FileWriter):
    def __init__(self, numbered=False, outputDir='.', multiSheetOutput=False, editMode=False, extension='.txt',
                   * supported: str):
        super().__init__(numbered, outputDir, multiSheetOutput, editMode, extension, * supported)
        self.sep = ' '

    def quote(self, s):
        return str(s)

    def join(self, iterable):
        """ join an iterable of any type to produce a String."""
        return self.sep.join(self.quote(x) for x in iterable)

    def _getopendoc(self):
        if self.multiSheetOutput:
            self.doc = open(self.getFilename(), 'w', encoding='utf-8')

    def openSheet(self, sheetname, sheetType=TEXT, **kwargs):
        super().openSheet(sheetname, sheetType)
        if not self.multiSheetOutput:
            self.doc = open(self.getSheetFilename(), 'w', encoding='utf-8')

    def _savedoc(self):
        close(self.doc)

    def writeRaw(self, *args: str, **kwargs):
        print(*(arg for arg in args), file=self.doc, **kwargs)

    def writeEncode(self, arg: Iterable, **kwargs): #arg: Union[str,iterable]
        if isinstance(arg,str):
            self.writeRaw(self.quote(arg), **kwargs)
        else:
            self.writeRaw(self.join(arg), **kwargs)

    def writeTitle(self, arg, **kwargs):
        self.writeEncode(arg, **kwargs)
        super().writeTitle(arg, **kwargs)

    def startNewLine(self):
        self.writeRaw(self.endline)

    def append(self, element, **kwargs):
        self.writeEncode(element, nl='', **kwargs)

    def writeln(self, iterable, **kwargs):
        self.writeEncode(iterable, **kwargs)
        super().writeln(iterable, **kwargs)

    def closeSheet(self):
        if not self.multiSheetOutput:
            close(self.doc)
        super().closeSheet()


availableWriters['txt'] = TextWriter(TEXT, TABLE, BIBLIOGRAPHY, LIST)
