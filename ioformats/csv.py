# import csv
from ioformats.filerw import FileWriter
from ioformats import availableWriters,TEXT,TABLE,BIBLIOGRAPHY

class CSVwriter(FileWriter):#<Iterable>
    def __init__(self, numbered=False, outputDir='.',multiSheetOutput=False,editMode=False,extension='.csv',sep=';'):
        super().__init__(numbered,multiSheetOutput,editMode)
        self.extension = extension
        self.sep = sep
        self.endline = ''

    def quote(self,s):
        return str(x)
    
    def join(self,iterable):
        ''' join an iterable of any type to produce a String.'''
        return self.sep.join(self.quote(x) for x in iterable)
    
    def open(self, filename):
        super().open(filename)
        if self.multiSheetOutput:
            self.doc = open(self.getFilename(), 'w', encoding='utf-8')

    
    def openSheet(self,sheetname,sheetType=TEXT,**kwargs):
        super().openSheet(sheetname,sheetType)
        if not self.multiSheetOutput:
            self.doc = open(self.getSheetFilename(), 'w', encoding='utf-8')

    def _savedoc(self,filename):
        close(self.doc)


    def writeEncode(self, *args):
        print(*(arg for arg in args),file=self.doc)

    def writeTitle(self,iterable,** kwargs): 
        self.writeEncode(self.join(iterable),self.endline)
        super().writeTitle(iterable,** kwargs)

    def writeln(self,iterable,** kwargs):
        self.writeEncode(self.join(iterable),self.endline)
        super().writeln(iterable,** kwargs)
        
    def closeSheet(self):
        super().closeSheet()
        self.wfile.close()
        self.wfile = None


availableWriters['csv'] = CSVwriter()
availableWriters['txt'] = CSVwriter(extension='.txt',sep='\t')
