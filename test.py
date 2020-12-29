import sys
import json

class testClass(object):
    headerDict = { "Name": 1, "Status": 2, "Title":3 }

    def addDelimitedItem(self, line, value, delimiter):
        newLine = line
        if newLine != "":
            newLine += delimiter
        newLine += value
        return newLine

    def setLineStatus(self, line, status):
        newLine = ""
        colList = line.split(';')
        for i,h in enumerate(self.headerDict):
            if h == 'Status':
                print('here 1')
                statusList = colList[i].split(',')
                newStatus = ""
                for s in statusList:
                    print(s)
                    if s != 'valid':
                        newStatus = self.addDelimitedItem(newStatus, s, ",")
                newStatus = self.addDelimitedItem(newStatus, status, ",")
                newLine = self.addDelimitedItem(newLine, newStatus, ";")
            else:
                newLine = self.addDelimitedItem(newLine, colList[i], ";")
        return newLine
    
if __name__ == "__main__":
    tc = testClass()
    newLine = tc.setLineStatus("abc;def,valid;ghi", "xyz")
    print(newLine)
