from ioformats.writers import AbstractWriter
from ioformats import availableWriters,TEXT,TABLE,BIBLIOGRAPHY

       
class GuiWriter(AbstractWriter):    
    def __init__(self, gui=None, numbered=False): 
        super().__init__(numbered)
        self.gui = gui
        self.col = 0
 
    def openSheet(self,sheetName,sheetType=TEXT,**kwargs):
        super().openSheet(sheetName,sheetType,**kwargs)
        self.currentSheet = self.gui.createTab(self.target, sheetName, sheetType)
        self.setLineNumber(0,TABLE)

    def writeTitle(self,iterable,** kwargs):
        self._writeln(iterable,True)
        self.setLineNumber(0)
        
    def writeln(self,iterable,** kwargs):
        self._writeln(iterable,False)

    def append(self,element,** kwargs):
        if self.sheetType == TABLE:
            self.gui.createCell(self.currentSheet,self.getCurrentLine(),self.col,element,False)
            self.col += 1
        elif self.sheetType == BIBLIOGRAPHY or self.sheetType == TEXT:
            self.gui.insertText(self.currentSheet,element)

    def startNewLine(self):
        self._incLineCount()
        if self.sheetType == TABLE:
             self.col = 0
        elif  self.sheetType == BIBLIOGRAPHY or self.sheetType == TEXT:
            self.gui.insertText(self.currentSheet,'\n'+self.getLinePrefix())
        

    def _writeln(self,iterable,isTitle):
        self.startNewLine()
        if self.sheetType == TABLE:
             self._writerow(iterable,isTitle)
        elif  self.sheetType == BIBLIOGRAPHY:
            self._writeBibItem(iterable)
        elif  self.sheetType == TEXT:
            self._writeText(iterable)

    def _writerow(self,iterable,isTitle):
        self.col = 0
        for v in iterable:
            if v != '':
                self.gui.createCell(self.currentSheet,self.getCurrentLine(),self.col,v,isTitle)
            self.col += 1

    def _writeBibItem(self,publication):
        self.gui.insertText(self.currentSheet,' '.join(str(x) for x in iterable)+'\n')

    def _writeText(self,iterable):
        self.gui.insertText(self.currentSheet,' '.join(str(x) for x in iterable)+'\n')



