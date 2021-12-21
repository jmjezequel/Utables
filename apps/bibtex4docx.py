import logging
import os
import sys
import tempfile
import csv
import unittest
from datetime import datetime

from openpyxl import load_workbook

from ioformats import TABLE,TEXT,BIBLIOGRAPHY,LIST
from ioformats.docxrw import DocxWriter
from ioformats.tex import TeXWriter, TeXTableReader
from ioformats.text import TextWriter
from ioformats.writers import AbstractWriter
from ioformats.xlsx import XlsxWriter

def clean_bib_entry(text: str):
    return text.replace('\\', '').replace('{', '').replace('},', '').replace('}', '').strip()

def clean_year_entry(text: str):
    return text.replace('"', '').replace('{', '').replace(',', '').replace('}', '').strip()

def parse_BibEntry(filename):
    result = {}
    lineCount = 0
    try:
        with open(filename,"r",encoding="utf-8") as f:
            for line in f:
                lineCount += 1
                line = line.strip()
                if len(line) > 0 and not line.startswith('%'):
                    if line.startswith('@'):
                        # new entry
                        sep = line.find('{')
                        if sep < 0:
                            print("Error in "+filename+", line "+str(lineCount)+": "+line)
                            exit(-1)
                        kind = line[1:sep].lower()
                        bibkey = line[sep+1:len(line)-1]
                        entry = BibEntry(kind, bibkey)
                        result[bibkey] = entry
                        key = None
                    else:
                        items = line.split('=')
                        if len(items) == 2:
                            key = items[0].strip().lower()
                            if key == "year":
                                entry.addData(key, clean_year_entry(items[1]))
                            else:
                                entry.addData(key, clean_bib_entry(items[1]))
                        else:  # no '=' found, try add more content to previous value
                            more = clean_bib_entry(line)
                            if more != '':
                                entry.addData(key, ' ' + more)
    except Exception as err:
        print("Error in " + filename + ", line " + str(lineCount) + ": " + line + ": "+ format(err))
        exit(-1)
    return result


class BibEntry:
    """ representing a bibtex entry"""

    def __init__(self, type, key):
        self.key = key
        self.type = type
        self._data = {}
        self._halId = ""

    def addData(self, key: str, value: str):
        if key in self._data:
            self._data[key] += value
        else:
            self._data[key] = value

    def getYear(self):
        return self._data.get("year")

    def getMonth(self):
        return self._data.get("month", 0)

    def getHalId(self):
        return self._halId

    def getCitationKey(self, keyStyle):
       return '[' + self.key + '] '

    def getAuthors(self):
        return self._data.get("author","")

    def getTitle(self):
        return self._data.get("title","")

    def getPublishers(self):
        p = self._data.get("publisher","")
        if p == "":
            p = self._data.get("organization", "")
        return p

    def getVenue(self):
        if self.isJournal() or self.isOutreach():
            venue = self._data.get("journal","")
            volume = self._data.get("volume",'')
            number = self._data.get("number",'')
            if number == '':
                number = self._data.get("issue",'')
            if number != '':
                volume += '('+number+')'
            return venue + ', ' + volume if volume != '' else venue
        booktitle = self._data.get("booktitle","")
        if booktitle == "":
            return ""
        if self.isConference():
            return booktitle
        if self.isBookChapter():
            return "In " + booktitle
        return ""

    def isJournal(self):
        return self.type == "article"

    def isOutreach(self):
        return self.type == "techreport"

    def isConference(self, internationalOnly=False):
        return self.type == "inproceedings"

    def isBookChapter(self):
        return self.type == "inbook"

    def isBook(self):
        return self.type == "book"

    def isThesis(self):
        return self.type == "phdthesis" or self.type == "masterthesis"

    def isEditedBook(self):
        return self.type == "book"

    def getFormatedAuthors(self, terse=False, maxTerseNumber=6):
        authors = self.getAuthors().split(" and ")
        count = len(authors)
        if count <= 0:
            return ""
        for n in range(0, count):
            parts = authors[n].split(',')
            if len(parts) > 1: # name is of the form: Name, Surname
                authors[n] = parts[1].strip() + ' ' + parts[0].strip()
        if terse:
            count = min(count, maxTerseNumber)
            result = getAbbrevAuthorName(authors[0])
            for n in range(1, count):
                result += ', '
                result += getAbbrevAuthorName(authors[n])
            if count < len(authors):
                result += ' et al'
            return result + '. '
        else:
            result = authors[0].strip()
            for n in range(1, count):
                result += ', ' if n < count - 1 else ' and '
                result += authors[n].strip()
            return result + '. '

    def __iter__(self):
        yield '['+self.key + ']'
        yield self.getFormatedAuthors()
 #       yield self.getAuthors()
        yield self.getTitle() + ','
        v = self.getVenue()
        if v != None and v != '':
            yield v + ','
        yield str(self.getYear()) + '.'

    def asString(self):
        return ' '.join(self)

    def write(self,writer,citationStyle=None,**kwargs):
        """ use writer to output this publication in biblio form.
        If citationStyle is not known it is interpreted as a function of this instance, e.g. pub.getHalId"""
        if citationStyle is not None:
            writer.append(self.getCitationKey(citationStyle),key=True)
        terse = kwargs.get('terse',False)
        writer.append(self.getFormatedAuthors(terse),authors=True)
        writer.append(self.getTitle(),title=True)
        v = self.getVenue()
        if v is not None and v != '':
            pages = self._data.get("pages","")
            if pages != "":
                v += ", pages "+pages.replace('--','-')
            writer.append(v + ', ')
        p = self.getPublishers()
        if p is not None and p != '':
            writer.append(p+', ')
        writer.append(str(self.getYear()) + '. ')
        # writer.append(MONTH_NAMES[terse][self.getMonth()]+str(self.getYear())+'. ')
        # writer.append(self.getHalId(), href=HALURL+self.getHalId())

MONTH_NAMES = {
    False: ['','January ','February ','March ','April ','May ','June ','July ','August ','September ','October ','November ','December '],
    True : ['','Jan. ','Fev. ','Mar. ','Apr. ','May ','Jun. ','Jul. ','Aug. ','Sep. ','Oct. ','Nov. ','Dec. ']
    }

def read_bib_keys(word: str, bibtex: dict):
    w = DocxWriter(multiSheetOutput=True, editMode=True)
    w.open(word)
    keys = list(set(w.yieldBibKeys("#bibtexlist")))
    keys.sort()
#    print(keys, sep=',')
    w.openSheet("#bibtexlist", BIBLIOGRAPHY, citationStyle="Key")
    for key in keys:
        if key in bibtex:
            print("Adding citation " + key)
            w.writeln(bibtex[key])
        else:
            print("Error: cannot find bibtex key "+key)
    w.closeSheet()
    w.close()



def main():
    if len(sys.argv) < 3:
        wordfile = "test.docx"
        bibtex = parse_BibEntry("test.bib")
    else: # test mode
        wordfile = sys.argv[1]
        bibtex = {}
        i = 2
        while (i<len(sys.argv)):
            bibtex.update(parse_BibEntry(sys.argv[i]))
            i += 1

#    for b in bibtex:
#        print(bibtex[b].asString())
    read_bib_keys(wordfile, bibtex)


if __name__ == "__main__":
    # execute only if run as a script
    main()

