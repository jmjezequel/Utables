from ioformats.writers import AbstractWriter
from ioformats import availableWriters,TEXT,TABLE,BIBLIOGRAPHY

    
class StringWriter(AbstractWriter):
    def __init__(self,numbered=False):
        super().__init__(numbered)
        self.result = {}

    def openSheet(self,sheetname,sheetType=TEXT):
        super().openSheet(sheetname,sheetType)
        self.result[sheetname] = ""

    def writeTitle(self,element,** kwargs): # always=false,level=1,insertMode=False,style=None
        self.writeln(element,** kwargs)
        
    def append(self,element,** kwargs):
        self.result[sheetname] += str(element)

    def writeln(self,iterable,** kwargs):
        line = self.getLinePrefix() + ' '.join(str(x) for x in iterable)
        line += '\n'
        self.result[sheetname] += line
        super().writeln(iterable,** kwargs)



#availableWriters['string'] = StringWriter()
#availableWriters['num-string'] = StringWriter(numbered=True)
