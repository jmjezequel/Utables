import itertools
from ioformats.csv import CSVwriter
from ioformats import availableWriters

specialTeXchars = {ord(c):'\\'+c for c in r'#\%_$^&'}
            
class TeXTableWriter(CSVwriter):
    def __init__(self,numbered=False, outputDir='.',multiSheetOutput=False,editMode=False):
        super().__init__(numbered,outputDir,multiSheetOutput,editMode,'.tex',sep = ' & ')
        self.endline = r'\\\line'

    def quote(self,s):
        return str(s).translate(specialTeXchars)

    #TODO: use subwriter (as in docx) for text, tables and biblio

#     def join(self,iterable):
#         ''' join an iterable of any type to produce a String suitable for inclusion in a TeX table'''
#         return ' & '.join(str(x).translate(TeXTableWriter.special) for x in iterable)+r"\\\hline"
    
    def _writeTitle(self,iterable,** kwargs): #TODO: should be called at first occurence of writetitel or writeln
        self.writeEncode(r"\label{"+self.target+'-'+self.normalize(self.sheetname)+'}')
        i1, i2 = itertools.tee(iterable, 2)    
        format = '|'.join('r' for i in i1)
        self.writeEncode(r"\begin{tabular}{|"+format.replace('r','l',1)+u'|}\hline')
        super().writeTitle(i2)

    def closeSheet(self):
        self.writeEncode(r"\end{tabular}") # close only if it was open by a write title
        super().closeSheet()

class BblWriter(CSVwriter):
    ''' write publis in the bbl expected format'''
    def __init__(self, terse=False):
        super().__init__(extension='.bbl',sep = '.')
        self.terse = terse

    def openSheet(self,sheetname):
        super().openSheet(sheetname)
        self.writeEncode(r'\begin{thebibliography}{100}')

    def writeTitle(self,iterable,always=False):
        self.writeEncode('% ',self.join(iterable))
       
    def writeln(self,pub,always=False):
        ''' WARNING: covariant definition of parameter: pub instead of iterable'''
        self.writeEncode(r'\bibitem{',pub.getKey(),'}')
        self.writeEncode(pub.getFormatedAuthors(self.terse).encode('UTF-8'))
        self.writeEncode(r'\newblock {',self.quote(pub.getTitle()),'}')
        self.writeEncode(r'\newblock ',self.quote(pub.getVenue()),', ',str(pub.getYear()),'.')
        self.currentline += 1

    def closeSheet(self):
        self.writeEncode(r'\end{thebibliography}')       
        super().closeSheet()

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
