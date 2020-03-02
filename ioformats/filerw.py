import unicodedata
import sys
import os
import re
from ioformats.writers import AbstractWriter

_pattern = re.compile("[^A-Za-z0-9_ ]+")

def normalize(name):
    if name == None:
        return None
    return _pattern.sub('',unicodedata.normalize('NFKD', name.strip()).encode('ascii','ignore').decode('ascii')).replace(' ','_').replace('__','_')

class FileWriter(AbstractWriter):
    ''' an abstract class for writers needing to deal with the file system'''
    def __init__(self,numbered=False,outputDir='.',multiSheetOutput=False,editMode=False):
        super().__init__(numbered)
        self._outputDir = outputDir
        self.multiSheetOutput = multiSheetOutput
        self.editMode = editMode
        self.doc = None
    
    def setOutputDir(self,outdir):
        self._outputDir = outdir
        os.makedirs(outdir, exist_ok=True)

    def getSheetFilename(self):
        ''' return filename, appended with normalized name of sheetName if !=None'''
        return self._outputDir+"/"+self.target+'-'+normalize(self.sheetName)+self.extension

    def getFilename(self):
        ''' return filename for saving'''
        return self._outputDir+"/"+self.target+self.extension
    
    def getBasename(self, filename):
        ''' return basename, without dir prefix and without file extension'''
        return os.path.basename(os.path.splitext(filename)[0])

    def _getopendoc(self,name=None):
        pass
    
    def _savedoc(self,filename):
        pass

    def open(self, filename):
        super().open(self.getBasename(filename))
        if not os.path.exists(filename):
            self.editMode = False #no file to read from, so force editMode to False
        if self.editMode:
            self.doc = self._getopendoc(filename)
        else:
            self.doc = self._getopendoc() # create a new instance of a document 
    
    def closeSheet(self):
        if not (self.editMode or self.multiSheetOutput):
            self._savedoc(self.getSheetFilename())
            self.doc = self._getopendoc() #restart from fresh doc
        super().closeSheet()

    def close(self):
        if self.editMode or self.multiSheetOutput:
            self._savedoc(self.getFilename())

