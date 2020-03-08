import itertools
from ioformats.csv import CSVwriter
from ioformats import availableWriters,TEXT,TABLE,BIBLIOGRAPHY,LIST
from ioformats.text import TextWriter
from ioformats.writers import SkipWriter

specialTeXchars = {ord(c):'\\'+c for c in r'#\%_$^&'}
            
class TeXWriter(TextWriter):
    def __init__(self,numbered=False, outputDir='.',multiSheetOutput=False,editMode=False):
        super().__init__(numbered,outputDir,multiSheetOutput,editMode,'.tex',TEXT,TABLE,BIBLIOGRAPHY,LIST)
        self.subwriter = PlainTextSubwriter(self)

    def quote(self,s):
        return str(s).translate(specialTeXchars)

    def open(self, filename):
        super().open(filename)
        if self.multiSheetOutput:
            self.writeEncode(r"\documentclass[11pt]{article}")
            self.writeEncode(r"\usepackage[T1]{fontenc}")
            self.writeEncode(r"\usepackage[utf8]{inputenc}")
            self.writeEncode(r"\begin{document}")
        else: # one file per sheet: change suffix according to subwriter
            self.extension = self.subwriter.getExtension()

    def close(self):
        if self.multiSheetOutput:
            self.writeEncode(r"\end{document}")
        super().close()

    def openSheet(self,sheetname,sheetType=TEXT,**kwargs):
        super().openSheet(sheetname,sheetType,**kwargs)
        self.subwriter = subwriters.get(sheetType,SkipWriter)(self)
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
        self.parent.endline = ''

    def closeSheet(self):
        pass

    def writeTitle(self, element, level=1, **kwargs):
        t = ARTICLE_TITLE_LEVELS[level] if level < len(ARTICLE_TITLE_LEVELS) else 'paragraph'
        self.parent.writeRaw('\\'+t+'{'+element+'}')
        if level == 0:
            self.parent.writeRaw(r"\maketitle")

    def startNewLine(self):
        self.parent.writeRaw('\n')

    def append(self, element, **kwargs):
        self.parent.writeEncode(element, **kwargs)

    def writeln(self, iterable, ** kwargs):
        self.parent.writeEncode(iterable, ** kwargs)

    def getExtension(self):
        return '.tex'


class TeXTableSubwriter():
    def __init__(self, parent=None):
        self.parent = parent
        self.col = 0

    def openSheet(self, sheetname, sheetType, **kwargs):
        self.parent.sep = ' & '
        self.parent.endline = r'\\\line'

    def _writeHeader(self,iterable,** kwargs):
        self.parent.writeRaw(r"\label{"+self.parent.target+'-'+self.parent.normalize(self.parent.sheetname)+'}')
        i1, i2 = itertools.tee(iterable, 2)    
        form = '|'.join('r' for i in i1)
        self.parent.writeRaw(r"\begin{tabular}{|" + form.replace('r', 'l', 1) + r'|}\hline')
        self.writeln(i2)

    def startNewLine(self):
        self.col = 0
        self.parent.writeRaw('\n')

    def append(self, element, **kwargs):
        if self.col > 0:
            self.parent.writeRaw('& ')
        self.parent.writeEncode(element, nl=' ', **kwargs)
        self.col += 1

    def writeln(self, iterable, ** kwargs):
        self.startNewLine()
        self.parent.writeEncode(iterable, ** kwargs)

    def closeSheet(self):
        self.parent.writeRaw(r"\end{tabular}")

    def getExtension(self):
        return '.tex'

class BblSubwriter(PlainTextSubwriter):
    """ write publis in the bbl expected format"""
    def __init__(self, parent=None):
        super().__init__(self,parent)
        self.kwargs = {}

    def openSheet(self,sheetname,sheetType,**kwargs):
        self.kwargs = kwargs
        self.parent.sep = ' '
        self.parent.endline = '.'
        self.parent.writeRaw(r'\begin{thebibliography}{100}')

    def closeSheet(self):
        self.parent.writeRaw(r'\end{thebibliography}')

    def writeTitle(self, element, level=1, **kwargs):
        if self.parent.multiSheetOutput:
            super().writeTitle(element, **kwargs)
        else:
            self.parent.writeRaw('% ',element)

    def writeln(self, publication, ** kwargs):
        """ WARNING: covariant definition of parameter: publication instead of iterable"""
        self.startNewLine()
        publication.write(self,**self.kwargs) # publication is going to call back append below

    def append(self,element, key=False, authors=False, title=False, venue=False, ** kwargs):
        if key:
            self.parent.writeRaw(r'\bibitem{', element, '}')
        elif authors:
            self.parent.writeRaw(element)
        elif title:
            self.parent.writeRaw(r'\newblock {', element, '}')
        elif venue:
            self.parent.writeRaw("In ", nl='')
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


#availableWriters['tex'] = TeXTableWriter()
#availableWriters['bbl'] = BblWriter()
subwriters = {TEXT:PlainTextSubwriter,TABLE:TeXTableSubwriter,BIBLIOGRAPHY:BblSubwriter}
