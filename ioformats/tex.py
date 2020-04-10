import itertools
from collections import Iterable
from datetime import datetime
import re

from ioformats import availableWriters,TEXT,TABLE,BIBLIOGRAPHY,LIST
from ioformats.filerw import normalize
from ioformats.text import TextWriter
from ioformats.writers import SkipWriter

specialTeXchars = {ord(c):'\\'+c for c in r'#\%_$^&'}
            
class TeXWriter(TextWriter):
    def __init__(self,numbered=False, outputDir='.',multiSheetOutput=False,editMode=False, *supported: str):
        super().__init__(numbered,outputDir,multiSheetOutput,editMode,'.tex', *supported)
        self.subwriter = PlainTextSubwriter(self)

    def quote(self,s):
        return str(s).translate(specialTeXchars)

    def open(self, filename):
        super().open(filename)
        if self.multiSheetOutput:
            self.writeRaw(r"\documentclass[11pt]{article}",'\n')
            self.writeRaw(r"\usepackage[T1]{fontenc}",'\n')
            self.writeRaw(r"\usepackage[utf8]{inputenc}",'\n')
            self.writeRaw(r"\begin{document}",'\n')
        else: # one file per sheet: change suffix according to subwriter
            self.extension = self.subwriter.getExtension()

    def close(self):
        if self.multiSheetOutput:
            self.writeRaw(r"\end{document}",'\n')
        super().close()

    def openSheet(self,sheetname,sheetType=TEXT,*args,**kwargs):
        self.subwriter = subwriters.get(sheetType,SkipWriter)(self)
        self.extension = self.subwriter.getExtension()
        super().openSheet(sheetname,sheetType,*args,**kwargs)
        self.subwriter.openSheet(sheetname,sheetType,**kwargs)

    def closeSheet(self):
        self.subwriter.closeSheet()
        super().closeSheet()

    def writeTitle(self, element, **kwargs):
        self.subwriter.writeTitle(element, **kwargs)

    def startNewLine(self):
        self.subwriter.startNewLine()

    def append(self, element, **kwargs):
        self.subwriter.append(element, **kwargs)

    def writeln(self, iterable, **kwargs):
        self.subwriter.writeln(iterable, **kwargs)

ARTICLE_TITLE_LEVELS = ['title','section','subsection','subsubsection','paragraph']
class PlainTextSubwriter():
    def __init__(self, parent=None):
        self.parent = parent

    def openSheet(self,sheetname,sheetType,**kwargs):
        self.parent.sep = ' '

    def closeSheet(self):
        pass

    def writeTitle(self, element, level=1, **kwargs):
        t = ARTICLE_TITLE_LEVELS[level] if level < len(ARTICLE_TITLE_LEVELS) else 'paragraph'
        if isinstance(element,str):
            title = element
        else:
            title = self.parent.join(element)
        self.parent.writeRaw('\\'+t+'{'+title+'}','\n')
        if level == 0:
            self.parent.writeRaw(r"\maketitle",'\n')

    def startNewLine(self):
        self.parent.writeRaw('\n')

    def append(self, element, italic=False, bold=False, **kwargs):
        if bold:
            self.parent.writeRaw(r'{\bf ')
        if italic:
            self.parent.writeRaw(r'{\it ')
        self.parent.writeEncode(element, **kwargs)
        if bold:
            self.parent.writeRaw('}')
        if italic:
            self.parent.writeRaw('}')

    def writeln(self, iterable, ** kwargs):
        self.append(iterable, ** kwargs)
        self.startNewLine()

    def getExtension(self):
        return '.tex'


class TeXTableSubwriter():
    def __init__(self, parent=None):
        self.parent = parent
        self.col = 0

    def openSheet(self, sheetname, sheetType, **kwargs):
        self.parent.sep = ' & '

    def _writeHeader(self,iterable,** kwargs):
        self.parent.writeRaw(r"\label{"+self.parent.target+'-'+normalize(self.parent.sheetName)+'}')
        i1, i2 = itertools.tee(iterable, 2)    
        form = '|'.join('r' for i in i1)
        self.parent.writeRaw(r"\begin{tabular}{|" + form.replace('r', 'l', 1) + r'|}\hline')
        self.writeln(i2)

    def writeTitle(self,element,** kwargs):
        """ write a title line onto table"""
        self._writeHeader(element,** kwargs)

    def startNewLine(self):
        self.col = 0
        self.parent.writeRaw('\n')

    def append(self, element, **kwargs):
        if self.col > 0:
            self.parent.writeRaw('& ')
        self.parent.writeEncode(element, **kwargs)
        self.col += 1

    def writeln(self, iterable, ** kwargs):
        self.startNewLine()
        self.parent.writeEncode(iterable, ** kwargs)
        self.parent.writeRaw(r'\\\hline')

    def closeSheet(self):
        self.startNewLine()
        self.parent.writeRaw(r"\end{tabular}")
        self.startNewLine()

    def getExtension(self):
        return '.tex'

class BblSubwriter(PlainTextSubwriter):
    """ write publis in the bbl expected format"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.kwargs = {}

    def openSheet(self,sheetname,sheetType,**kwargs):
        self.kwargs = kwargs
        self.parent.sep = ' '
        self.parent.writeRaw(r'\begin{thebibliography}{100}')

    def closeSheet(self):
        self.parent.writeRaw(r'\end{thebibliography}',end='\n')

    def writeTitle(self, element, level=1, **kwargs):
        if self.parent.multiSheetOutput:
            super().writeTitle(element, **kwargs)
        else:
            self.parent.writeRaw('% ',element)

    def writeln(self, publication, ** kwargs):
        self.startNewLine()
        publication.write(self,**self.kwargs) # publication is going to call back append below
        self.startNewLine()

    def append(self,element, key=False, authors=False, title=False, venue=False, ** kwargs):
        if key:
            self.parent.writeRaw(r'\bibitem{', element, '} ')
        elif authors:
            self.startNewLine()
            self.parent.writeRaw(element,'.')
        elif title:
            self.startNewLine()
            self.parent.writeRaw(r'\newblock {', element, '}. ')
        elif venue:
            self.startNewLine()
            self.parent.writeRaw(r'\newblock')
            self.parent.writeRaw("In ")
            self.parent.writeEncode(element)
        else:
            self.parent.writeEncode(element)

    def getExtension(self):
        return '.bbl'

# \begin{thebibliography}{10}
# 
# \bibitem{degueule:hal-01424909}
# Thomas Degueule, Benoit Combemale, and Jean-Marc J{\'e}z{\'e}quel.
# \newblock {On Language Interfaces}.
# \newblock In Bertrand Meyer and Manuel Mazzara, editors, {\em {PAUSE: Present
#   And Ulterior Software Engineering}}. {Springer}, February 2017.
# \end{thebibliography}


class ListSubwriter(PlainTextSubwriter):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.kind = 'itemize'

    def openSheet(self,sheetname,sheetType,**kwargs):
        self.kind = 'enumerate' if self.parent.isNumbered() else 'itemize'
        self.parent.sep = ' '
        self.parent.writeRaw(r'\begin{',self.kind,'}','\n')

    def closeSheet(self):
        self.parent.writeRaw(r'\end{'+self.kind+'}','\n')

    def writeTitle(self,element,** kwargs):
        """ there should be no title in a list, write it as a comment"""
        self.parent.writeRaw('% ')
        super().writeln(element,**kwargs)


    def writeln(self,iterable,** kwargs):
        self.parent.writeRaw(r'\item ')
        super().writeln(iterable,**kwargs)

availableWriters['tex'] = TeXWriter()
availableWriters['latex-article'] = TeXWriter(multiSheetOutput=True)
availableWriters['bbl'] = TeXWriter(True,'.',False,False,BIBLIOGRAPHY)
subwriters = {TEXT:PlainTextSubwriter,TABLE:TeXTableSubwriter,LIST:ListSubwriter,BIBLIOGRAPHY:BblSubwriter}


class TeXTableReader():
    def __init__(self,source: Iterable):
        self.source = source
        self.inside_table = False

    def __iter__(self):
        for line in self.source:
            if self.inside_table:
                if line.find(r'\end{tabular}')>=0:
                    self.inside_table = False
                    break
                else:
                    yield self.getArray(line)
            elif line.find(r'\begin{tabular}')>=0:
                self.inside_table = True

    def getArray(self, line):
        AS = '%%ampsand%%'
        line = line.replace(r'\&',AS)
        result = line.rstrip('hline\n').replace('\\','').split('&')
        return list(guess_type(e.strip().replace(AS,r'&')) for e in result)



def guess_type(s):
    if re.match("\A[-0-9]+\.[0-9]+\Z", s):
        return float(s)
    elif re.match("\A[-0-9]+\Z", s):
        return int(s)
    # 2019-01-01 or 01/01/2019 or 01/01/19
    elif re.match("\A[0-9]{4}-[0-9]{2}-[0-9]{2}\Z", s.split(' ')[0]) or \
            re.match("\A[0-9]{2}/[0-9]{2}/([0-9]{2}|[0-9]{4})\Z", s):
        return datetime.fromisoformat(s)
    elif re.match("\A(true|false)\Z", s):
        return bool(s)
    else:
        return s

