import logging

from ioformats import availableWriters,TEXT,TABLE,BIBLIOGRAPHY


class AbstractWriter():
    def __init__(self,numbered=False):
        self.target = None #TODO: rename docName
        self.currentSheet = None
        self.sheetType = None
        self.sheetName = '' #TODO rename ??
        self.currentline = {}
        self.numberPrefix = '['
        self.numberSuffix = '] '
        self.setLineNumber(0 if numbered else -1,TEXT,TABLE,BIBLIOGRAPHY) #-1 stands for no line count for this type

    def setLineNumber(self, value: int, * types):
        ''' Enable line counting at value=value for each type in types, unless value=-1'''
        if len(types) == 0: # set the current type
            self.currentline[self.sheetType] = value
        else:
            for type in types:
                self.currentline[type] = value

    def resetLineNumber(self, * types):
        if types == None:
            types = self.currentline.key()
        for type in types:
            self.currentline[type] = 0 if self.currentline[type]>=0 else -1 # reset to either 0 if counted, or -1 if
            # not numbered

    def isNumbered(self):
        return self.currentline[self.sheetType] >= 0
    
    def getCurrentLine(self):
        return self.currentline[self.sheetType]
    
    def getSupportedTypes(self):
        return self.currentline.keys()
    
    def getLinePrefix(self):
        return self.numberPrefix+str(self.getCurrentLine())+self.numberSuffix if self.isNumbered() else ""
        
    def open(self, target: str):
        self.target = target
        self.resetLineNumber()
        self.sheetName = None #TDODO: rename

    def openSheet(self, sheetName: str, sheetType=TEXT, numbered=False, resetCount=True, **kargs): #TODO: rename ???
        self.sheetName = sheetName
        if sheetType in self.getSupportedTypes():
            self.sheetType = sheetType
        else:
            logging.warning('Unsupported Sheet Type: '+sheetType+' for '+sheetName+'; Reverting to text.')
            self.sheetType = TEXT
        if resetCount: # not that resetCount => numbered
            self.currentline[self.sheetType] = 0
        elif not numbered:
            self.currentline[self.sheetType] = -1

    def _incLineCount(self):
        '''increment line count only if enabled i.e. > -1'''
        if self.currentline[self.sheetType] > -1:
            self.currentline[self.sheetType] += 1
        
    def writeTitle(self,element,** kwargs): # always=false,level=1,insertMode=False,style=None
        self.startNewLine()
        
    def append(self,element,** kwargs):
        pass
    
    def writeln(self,element,** kwargs): 
        self.startNewLine()

    def startNewLine(self): 
        self._incLineCount()
    
    def closeSheet(self):
        self.sheetName = ''

    def close(self):
        pass

class SkipWriter(AbstractWriter):
    def __init__(self,*args,**kargs):
        pass

    def openSheet(self,*args,**kargs):
        pass

    def closeSheet(self):
        pass
    
    def writeTitle(self,element,** kwargs): 
        pass

    def append(self,* element,** kwargs):
        pass
        
    def startNewLine(self): 
        pass
    
    def writeln(self,iterable,** kwargs):
        pass

class ConsoleWriter(AbstractWriter):#<Iterable>
    def __init__(self, numbered=False): 
        super().__init__(numbered)

    def writeTitle(self,element,** kwargs): # always=false,level=1,insertMode=False,style=None
        if isinstance(element,str):
            print(self.getLinePrefix()+element)
        else:
            self.writeln(iterable,** kwargs)

    def append(self,element,** kwargs):
        print(element,nl='')

    def startNewLine(self):
        print()
        self._incLineCount()
        print(self.getLinePrefix(),nl='')

    def writeln(self,iterable,** kwargs):
        self._incLineCount()
        print(self.getLinePrefix()+'\t'.join(str(x) for x in iterable))

availableWriters['console'] = ConsoleWriter()
 

class MultiWriter(AbstractWriter):
    ''' multiplex several other writers'''
    def __init__(self, numbered=False, * subwriterNames):
        super().__init__(numbered)
        self._subwriters = map(lambda key: availableWriters[key],subwriterNames)

    def add(self, * subwriters):
        self._subwriters.extend(subwriters)

    def open(self, target):
        super().open(target)
        map(lambda s: s.open(target), self._subwriters)

    def openSheet(self, *args, **kargs):
        super().openSheet(*args, **kargs)
        map(lambda s: s.openSheet(*args, **kargs), self._subwriters)

    def writeTitle(self, element, **kwargs):
        super().writeTitle(element, **kwargs)
        map(lambda s: s.writeTitle(element, **kwargs), self._subwriters)

    def append(self, *element, **kwargs):
        super().append(*element, **kwargs)
        map(lambda s: s.append(*element, **kwargs), self._subwriters)

    def startNewLine(self):
        super().startNewLine()
        map(lambda s: s.startNewLine(), self._subwriters)

    def writeln(self,iterable,**kwargs):
        cache = list(iterable) #to avoid recomputations
        super().writeln(iterable, **kwargs)
        map(lambda s: s.writeln(cache, **kwargs), self._subwriters)
        
    def closeSheet(self):
        map(lambda s: s.closeSheet(), self._subwriters)
        super().closeSheet()
        
    def close(self):
        map(lambda s: s.close(), self._subwriters)
        super().close()
 
availableWriters['multi'] = MultiWriter()

def getWriter(key,**kwargs):
    w = availableWriters[key]
    for att,value in kwargs.item():
        setattr(w, att, value)
    return w


