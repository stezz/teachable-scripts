# coding: utf8
import codecs
import sys

class Writer:
    def __init__(self):
        self.data = []
        self.currentLine = None
        self.separator = ','

    def startNewLine(self):
        if self.currentLine:
            self.endCurrentLine()
        self.currentLine = []

    def endCurrentLine(self):
        if self.currentLine:
            self.data.append(self.currentLine)
        self.currentLine = None

    def addFullLineString(self,fullline):
        self.startNewLine()
        self.addItem(fullline)
        self.endCurrentLine()

    def addItem(self,item):
        if not self.currentLine:
            self.startNewLine()
        self.currentLine.append(item.encode('utf-8'))

    def writeOutput(self):
        if self.currentLine:
            self.endCurrentLine()
        self._prepareOutput()
        for line in self.data:
            firstItem = True
            for column in line:
                if firstItem:
                    separator = ''
                    firstItem = False
                else:
                    separator = self.separator
                self._writeItem(column, separator)
            self._writeEndOfLine()
        self._closeOutput()

    def _prepareOutput(self):
        print("")

    def _writeItem(self,item, separator):
        sys.stdout.write(separator + item.decode('utf-8'))

    def _writeEndOfLine(self):
        print("")

    def _closeOutput(self):
        print('')


class FileWriter(Writer):
    def __init__(self, filePath):
        Writer.__init__(self)
        self.filePath = filePath
        self.file = None

    def _prepareOutput(self):
        self.file = codecs.open(self.filePath,'w', 'utf-8')

    def _writeItem(self,item, separator):
        self.file.write(separator + item.decode('utf-8'))
    def _writeEndOfLine(self):
        self.file.write('\n')

    def _closeOutput(self):
        self.file.close()


class CSVFileWriter(FileWriter):
    def __init__(self, filePath, csvSeparator):
        FileWriter.__init__(self,filePath)
        self.separator = csvSeparator
