import os

class Model:
    '''To be subclassed to implement actual save and load'''
    def __init__(self,fileExtension):
        self.fileExtension=fileExtension
        self.filename = None
        self.dirty = False

    def isDirty(self):
        return self.dirty

    def isNew(self):
        return self.filename == None

    def reset(self):
        self.filename = None
        self.dirty = False

    def loadFrom(self,file):
        self.load(file)
        self.filename = file.name
        self.dirty = False
        file.close

    def _saveTo(self,file):
        self.save(file)
        self.dirty = False
        file.close

    def saveTo(self,file):
        self.filename = file.name
        self._saveTo(file)

    def resave(self):
        file = open(self.filename, 'w+')
        self._saveTo(file)
