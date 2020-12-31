import traceback
import sys 
import subprocess
import os.path
import json
##import progress

from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PyQt5.QtWidgets import *
from PyQt5.Qt import *
from ProgressDialog import ProgressDialog
from AmConfig import AmConfig

class Ui_Dialog(QWidget):
    fileHeader = str()
    lineDict = dict()
    gameDict = dict()
    headerDict = dict()
    configData = AmConfig()
    configfile = 'AttractModeMameListMgr.cfg'
    romPath = ""
    firstLoad = True

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(768, 470)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.dupBtn = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dupBtn.sizePolicy().hasHeightForWidth())
        self.dupBtn.setSizePolicy(sizePolicy)
        self.dupBtn.setObjectName("dupBtn")
        self.gridLayout.addWidget(self.dupBtn, 4, 3, 1, 1)
        self.ptxt = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ptxt.sizePolicy().hasHeightForWidth())
        self.ptxt.setSizePolicy(sizePolicy)
        self.ptxt.setAlignment(QtCore.Qt.AlignCenter)
        self.ptxt.setObjectName("ptxt")
        self.gridLayout.addWidget(self.ptxt, 4, 10, 1, 1)
        self.mameExe = QtWidgets.QLineEdit(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mameExe.sizePolicy().hasHeightForWidth())
        self.mameExe.setSizePolicy(sizePolicy)
        self.mameExe.setMinimumSize(QtCore.QSize(500, 0))
        self.mameExe.setObjectName("mameExe")
        self.gridLayout.addWidget(self.mameExe, 1, 1, 1, 7)
        self.amDir = QtWidgets.QLineEdit(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.amDir.sizePolicy().hasHeightForWidth())
        self.amDir.setSizePolicy(sizePolicy)
        self.amDir.setMinimumSize(QtCore.QSize(500, 0))
        self.amDir.setObjectName("amDir")
        self.gridLayout.addWidget(self.amDir, 0, 1, 1, 7)
        self.treeWidget = QtWidgets.QTreeWidget(Dialog)
        self.treeWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.treeWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.treeWidget.setColumnCount(4)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "1")
        self.treeWidget.headerItem().setText(1, "2")
        self.treeWidget.headerItem().setText(2, "3")
        self.treeWidget.headerItem().setText(3, "4")
        self.gridLayout.addWidget(self.treeWidget, 3, 0, 1, 11)
        self.cloneBtn = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cloneBtn.sizePolicy().hasHeightForWidth())
        self.cloneBtn.setSizePolicy(sizePolicy)
        self.cloneBtn.setObjectName("cloneBtn")
        self.gridLayout.addWidget(self.cloneBtn, 4, 4, 1, 1)
        self.expColBtn = QtWidgets.QPushButton(Dialog)
        self.expColBtn.setObjectName("expColBtn")
        self.gridLayout.addWidget(self.expColBtn, 1, 10, 1, 1)
        self.loadListBtn = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.loadListBtn.sizePolicy().hasHeightForWidth())
        self.loadListBtn.setSizePolicy(sizePolicy)
        self.loadListBtn.setObjectName("loadListBtn")
        self.gridLayout.addWidget(self.loadListBtn, 4, 0, 1, 1)
        self.mameExeLbl = QtWidgets.QLabel(Dialog)
        self.mameExeLbl.setObjectName("mameExeLbl")
        self.gridLayout.addWidget(self.mameExeLbl, 1, 0, 1, 1)
        self.mameExeBtn = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mameExeBtn.sizePolicy().hasHeightForWidth())
        self.mameExeBtn.setSizePolicy(sizePolicy)
        self.mameExeBtn.setMaximumSize(QtCore.QSize(25, 16777215))
        self.mameExeBtn.setObjectName("mameExeBtn")
        self.gridLayout.addWidget(self.mameExeBtn, 1, 8, 1, 1)
        self.amDirBtn = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.amDirBtn.sizePolicy().hasHeightForWidth())
        self.amDirBtn.setSizePolicy(sizePolicy)
        self.amDirBtn.setMaximumSize(QtCore.QSize(25, 16777215))
        self.amDirBtn.setObjectName("amDirBtn")
        self.gridLayout.addWidget(self.amDirBtn, 0, 8, 1, 1)
        self.saveConfigBtn = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.saveConfigBtn.sizePolicy().hasHeightForWidth())
        self.saveConfigBtn.setSizePolicy(sizePolicy)
        self.saveConfigBtn.setObjectName("saveConfigBtn")
        self.gridLayout.addWidget(self.saveConfigBtn, 0, 10, 1, 1)
        self.amDirLbl = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.amDirLbl.sizePolicy().hasHeightForWidth())
        self.amDirLbl.setSizePolicy(sizePolicy)
        self.amDirLbl.setObjectName("amDirLbl")
        self.gridLayout.addWidget(self.amDirLbl, 0, 0, 1, 1)
        self.startBtn = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.startBtn.sizePolicy().hasHeightForWidth())
        self.startBtn.setSizePolicy(sizePolicy)
        self.startBtn.setObjectName("startBtn")
        self.gridLayout.addWidget(self.startBtn, 4, 5, 1, 1)
        self.saveMameBtn = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.saveMameBtn.sizePolicy().hasHeightForWidth())
        self.saveMameBtn.setSizePolicy(sizePolicy)
        self.saveMameBtn.setObjectName("saveMameBtn")
        self.gridLayout.addWidget(self.saveMameBtn, 4, 1, 1, 1)
        self.lockBtn = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lockBtn.sizePolicy().hasHeightForWidth())
        self.lockBtn.setSizePolicy(sizePolicy)
        self.lockBtn.setObjectName("lockBtn")
        self.gridLayout.addWidget(self.lockBtn, 4, 6, 1, 1)
        self.searchLabel = QtWidgets.QLabel(Dialog)
        self.searchLabel.setObjectName("searchLabel")
        self.gridLayout.addWidget(self.searchLabel, 2, 0, 1, 1)
        self.searchLine = QtWidgets.QLineEdit(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.searchLine.sizePolicy().hasHeightForWidth())
        self.searchLine.setSizePolicy(sizePolicy)
        self.searchLine.setMinimumSize(QtCore.QSize(500, 0))
        self.searchLine.setObjectName("searchLine")
        self.gridLayout.addWidget(self.searchLine, 2, 1, 1, 7)
        self.searchBtn = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.searchBtn.sizePolicy().hasHeightForWidth())
        self.searchBtn.setSizePolicy(sizePolicy)
        self.searchBtn.setMaximumSize(QtCore.QSize(25, 16777215))
        self.searchBtn.setObjectName("searchBtn")
        self.gridLayout.addWidget(self.searchBtn, 2, 8, 1, 1)
        self.clearSearchBtn = QtWidgets.QPushButton(Dialog)
        self.clearSearchBtn.setObjectName("clearSearchBtn")
        self.gridLayout.addWidget(self.clearSearchBtn, 2, 10, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 9, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 9, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 2, 9, 1, 1)
        
        self.treeWidget.headerItem().setText(0, "Game")
        self.treeWidget.headerItem().setText(1, "Variation")
        self.treeWidget.headerItem().setText(2, "Rom")
        self.treeWidget.headerItem().setText(3, "CloneOf")
        self.treeWidget.headerItem().setText(4, "Status")
        self.treeWidget.headerItem().setText(5, "Locked")
        
        self.amDirBtn.clicked.connect(self.openAmDirDialog)
        self.startBtn.clicked.connect(self.processList)
        self.loadListBtn.clicked.connect(self.loadList)
        self.saveConfigBtn.clicked.connect(self.saveConfig)
        self.mameExeBtn.clicked.connect(self.openMameExeDialog)
        self.saveMameBtn.clicked.connect(self.saveMame)
        self.dupBtn.clicked.connect(self.findDuplicates)
        self.cloneBtn.clicked.connect(self.unselectClones)
        self.expColBtn.clicked.connect(self.expColTree)
        self.lockBtn.clicked.connect(self.toggleLock)
        self.searchBtn.clicked.connect(self.searchList)
        self.clearSearchBtn.clicked.connect(self.clearSearch)
        self.searchLine.textEdited.connect(self.searchLineClicked);
        self.setTabOrder(self.searchLine, self.searchBtn)
#        self.searchLine.focusSignal.connect(self.
        
        self.treeWidget.setSortingEnabled(True)

        self.retranslateUi(Dialog)

        Dialog.setWindowFlags(Dialog.windowFlags() |
            QtCore.Qt.WindowMinimizeButtonHint |
            QtCore.Qt.WindowMaximizeButtonHint)

        QtCore.QMetaObject.connectSlotsByName(Dialog)
        if os.path.exists(self.configfile):
            self.configData.loadJSON(self.configfile)
            self.amDir.setText(self.configData.amDir)
            self.mameExe.setText(self.configData.mameExe)
            
        self.loadListBtn.setFocus(Qt.NoFocusReason)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "AttractMode Mame List Manager"))
        self.dupBtn.setText(_translate("Dialog", "Find Duplicates"))
        self.ptxt.setText(_translate("Dialog", "TextLabel"))
        self.treeWidget.setSortingEnabled(True)
        self.cloneBtn.setText(_translate("Dialog", "Unselect Clones"))
        self.expColBtn.setText(_translate("Dialog", "Expand"))
        self.loadListBtn.setText(_translate("Dialog", "Load Mame.txt"))
        self.mameExeLbl.setText(_translate("Dialog", "Mame Executable"))
        self.mameExeBtn.setText(_translate("Dialog", "..."))
        self.amDirBtn.setText(_translate("Dialog", "..."))
        self.saveConfigBtn.setText(_translate("Dialog", "Save Config"))
        self.amDirLbl.setText(_translate("Dialog", "AttractMode Directory"))
        self.startBtn.setText(_translate("Dialog", "Validate"))
        self.saveMameBtn.setText(_translate("Dialog", "Save Mame.txt"))
        self.lockBtn.setText(_translate("Dialog", "Lock Selected"))
        self.searchLabel.setText(_translate("Dialog", "Search"))
        self.searchBtn.setText(_translate("Dialog", "Go"))
        self.clearSearchBtn.setText(_translate("Dialog", "Clear Search"))

    def searchLineClicked(self):
        self.searchBtn.setDefault(True)
        self.searchBtn.setAutoDefault(True)
        
    def toggleLock(self):
        try:
            getSelected = self.treeWidget.selectedItems()
            if getSelected:
                baseNode = getSelected[0]
                if baseNode.text(5) == "Yes":
                    baseNode.setText(5,"No")
                else:
                    baseNode.setText(5,"Yes")
        except:
            traceback.print_exc()

    def setTreeHidden(self, hidden):
        root = self.treeWidget.invisibleRootItem()
        titleCount = root.childCount()
        for idx in range(titleCount):
            item = root.child(idx)
            item.setHidden(hidden)
            for cIdx in range(item.childCount()):
                child = item.child(cIdx)
                child.setHidden(hidden)
        
    def clearSearch(self):
        self.setTreeHidden(False)
        
    def searchList(self):
        if self.searchLine.text() != "":
            self.setTreeHidden(True)

            resultItems = self.treeWidget.findItems(self.searchLine.text(), QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive, 0)
            for item in resultItems:
                item.setHidden(False)
                if item.parent():
                    item.parent().setHidden(False)
            
    def getRomPath(self, fileToOpen):
        if os.path.isfile(fileToOpen):
            romPath = ""
            with open(fileToOpen, "r") as fp:
                line = fp.readline()
                while line:
                    keyVal = ' '.join(line.split()).split(' ')
                    if keyVal[0] == 'rompath':
                        romPath = keyVal[1]
                        break
                    line = fp.readline()
            return romPath
        else:
            return "Invalid Path"
            
    def expColTree(self):
        try:
            if self.expColBtn.text() == "Expand":
                self.treeWidget.expandAll()
                self.expColBtn.setText("Collapse")
            else:
                self.treeWidget.collapseAll()
                self.expColBtn.setText("Expand")
        except:
            traceback.print_exc()
            
    def saveConfig(self):
        self.configData.amDir = self.amDir.text()
        self.configData.mameExe = self.mameExe.text()
        self.configData.saveJSON(self.configfile)

    def getLineCount(self):
        lineCnt = 0
        fileToOpen = os.path.join(self.amDir.text(), "romlists\\Mame.txt")
        with open(fileToOpen) as fp:
            line = fp.readline()
            while line:
                lineCnt += 1
                line = fp.readline()

        fp.close()
        return lineCnt

    def openAmDirDialog(self):
        try:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fileName = str(QFileDialog.getExistingDirectory())
        except:
            print("Oops!", sys.exc_info()[0], "occurred.")
        if fileName:
            self.amDir.setText(os.path.normpath(fileName))

    def openMameExeDialog(self):
        try:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            dirName = os.path.dirname(os.path.realpath(self.mameExe.text()))
            if os.path.isdir(dirName):
                tempDir = dirName
            else:
                tempDir = 'c:\\'
            fileName, _ = QFileDialog.getOpenFileName(self, 'Mame Exe', tempDir, "Exe files (*.exe)")
        except:
            print("Oops!", sys.exc_info()[0], "occurred.")
        if os.path.isfile(fileName):
            self.mameExe.setText(os.path.normpath(fileName))

    def addDelimitedItem(self, line, value, delimiter):
        newLine = line
        if newLine != "":
            newLine += delimiter
        newLine += value
        return newLine

    def getFieldValue(self, field, delimiter, validValues):
        valueList = field.split(delimiter)
        fieldValue = ""
        for v in valueList:
            if v in validValues:
                return v

    def setLineStatus(self, line, status):
        if status == '':
            newLine = line
        else:
            newLine = ""
            colList = line.split(';')
            for i,h in enumerate(self.headerDict):
                if h == 'Status':
                    statusList = colList[i].split(',')
                    newStatus = ""
                    for s in statusList:
                        if s != 'pass' and s != 'fail':
                            newStatus = self.addDelimitedItem(newStatus, s, ",")
                    newStatus = self.addDelimitedItem(newStatus, status, ",")
                    newLine = self.addDelimitedItem(newLine, newStatus, ";")
                else:
                    newLine = self.addDelimitedItem(newLine, colList[i], ";")
        return newLine

    def removeFieldVal(self, field, val):
        if val == '':
            return field
        newField = ""
        valList = field.split(',')
        for j in valList:
            if j != val:
                newField = self.addDelimitedItem(newField, j, ",")
        return newField

    def addFieldVal(self, field, val):
        if val == '':
            return field
        newField = field
        valList = field.split(',')
        for j in valList:
            if j == val:
                return newField
        newField = self.addDelimitedItem(newField, val, ",")
        return newField

    def setFieldVal(self, line, field, addVal, remVal):
        newLine = ""
        colList = line.split(';')
        for i, h in enumerate(self.headerDict):
            newField = colList[i]
            if h == field:
                newField = self.removeFieldVal(newField, remVal)
                newField = self.addFieldVal(newField, addVal)
            newLine = self.addDelimitedItem(newLine, newField, ';')
        return newLine

    def updateLineDict(self):
        root = self.treeWidget.invisibleRootItem()
        titleCount = root.childCount()        
        pIdx = 0
        for idx in range(titleCount):
            item = root.child(idx)
            for cIdx in range(item.childCount()):
                pIdx += 1
                child = item.child(cIdx)
                romname = child.text(2)
                status = child.text(4)
                locked = child.text(5)
                newLine = self.setLineStatus(self.lineDict[romname], status)
                if child.checkState(0) == QtCore.Qt.Checked:
                    newLine = self.setFieldVal(newLine, 'Extra', '', 'excluded')
                else:
                    newLine = self.setFieldVal(newLine, 'Extra', 'excluded', '')
                if locked == 'Yes':
                    newLine = self.setFieldVal(newLine, 'Extra', 'locked', '')
                else:
                    newLine = self.setFieldVal(newLine, 'Extra', '', 'locked')
                self.lineDict[romname] = newLine

    def saveMame(self):
        try:
            if len(self.lineDict) > 0:
                self.updateLineDict()
                fileToOpen = os.path.join(self.amDir.text(), "romlists\\Mame.txt")
                with open(fileToOpen, "w") as of:
                    of.write(self.fileHeader)
                    for line in sorted(self.lineDict.values(), key = lambda kv:kv.split(';')[self.headerDict['Title']]):
                        of.write(line+'\n')
            
        except:
            traceback.print_exc()

    def getVariation(self, title):
        try:
            var = ''
            begIdx = -1
            endIdx = -1
            newBegIdx = -1
            depth = 0
            newTitle = title
            for i in reversed(range(len(title))):
                if title[i] == ')':
                    depth += 1
                    if endIdx == -1:
                        endIdx = i
                elif title[i] == '(':
                    depth -= 1
                    if depth == 0:
                        begIdx = i
                        if var != "":
                            var = ' - ' + var.strip()
                        var = title[begIdx+1:endIdx] + var
                        newBegIdx = begIdx
                        endIdx = -1
                        begIdx = -1
            if newBegIdx > 0:
                newTitle = title[0:newBegIdx-1].strip()
        except:
            traceback.print_exc()
            raise e
        return var, newTitle;

    def addParent(self, treeItem, newTitle, romname):
        gameIdx = self.treeWidget.topLevelItemCount()
        self.gameDict[romname] = gameIdx
        self.treeWidget.addTopLevelItem(QTreeWidgetItem(gameIdx))
        treeItem = self.treeWidget.topLevelItem(gameIdx)
        treeItem.setFlags(treeItem.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsTristate)
        treeItem.setText(0, newTitle)
        return treeItem

    def addChild(self, treeItem, newTitle, variation, romname, cloneOf, status, extra):
        childItem = QTreeWidgetItem()
        extraList = extra.split(',')
        checked = ''
        locked = False
        for c in extraList:
            if c == 'excluded':
                checked = c
            if c == 'locked':
                locked = True
        if checked == 'excluded':
            childItem.setCheckState(0, Qt.Unchecked)
        else:
            childItem.setCheckState(0, Qt.Checked)

        if locked:
            childItem.setText(5, 'Yes')

        childItem.setText(0, newTitle)
        childItem.setText(1, variation)
        childItem.setText(2, romname)
        childItem.setText(3, cloneOf)
        childItem.setText(4, status)
        
        treeItem.insertChild(treeItem.childCount(), childItem)

    def getStatus(self, status):
        statusList = status.split(',')
        status = ''
        for s in statusList:
            if s == 'pass' or s == 'fail':
                status = s        
        return status
    
    def loadTree(self):
        romnameCol = self.headerDict['Name']
        titleCol   = self.headerDict['Title']
        cloneofCol = self.headerDict['CloneOf']
        statusCol  = self.headerDict['Status']
        try:
            d = QtWidgets.QDialog()
            dui = ProgressDialog()
            dui.setupUi(d)
            d.show()
            dui.setProgressRange(1, len(self.lineDict))
        except:
            traceback.print_exc()

        idx = 0
        
        for romname, line in self.lineDict.items():
            if dui.isCancelled() == True:
                break;
            wordlist = line.strip('\n\r').split(';')
            cloneOf = wordlist[cloneofCol]

            if cloneOf == "":
                try:
                    title   = wordlist[titleCol]
                    status  = self.getStatus(wordlist[statusCol])
                    extra = wordlist[self.headerDict['Extra']]
                    variation, newTitle = self.getVariation(title)
                    treeItem = self.addParent(self.treeWidget, newTitle, romname)
                    self.addChild(treeItem, newTitle, variation, romname, cloneOf, status, extra)
                    idx += 1
                    dui.setProgressValue(idx)
                    if idx%100 == 0:
                        app.processEvents()
                except:
                    traceback.print_exc()
                    exit()

        for romname, line in self.lineDict.items():
            if dui.isCancelled() == True:
                break;
            wordlist = line.strip('\n\r').split(';')
            cloneOf = wordlist[cloneofCol]

            if cloneOf != "":
                try:
                    title   = wordlist[titleCol]
                    status  = self.getStatus(wordlist[statusCol])
                    extra = wordlist[self.headerDict['Extra']]
                    variation, newTitle = self.getVariation(title)
                    if cloneOf in self.gameDict.keys():
                        gameIdx = self.gameDict[cloneOf];
                        treeItem = self.treeWidget.topLevelItem(gameIdx)
                    else:
                        treeItem = self.addParent(self.treeWidget, cloneOf, cloneOf)
                    self.addChild(treeItem, newTitle, variation, romname, cloneOf, status, extra)
                    idx += 1
                    dui.setProgressValue(idx)
                    if idx%100 == 0:
                        app.processEvents()
                    app.processEvents()
                except:
                    traceback.print_exc()
                    exit()
        
    def loadList(self):
        validCnt = 0
        cnt = self.getLineCount()-1

        try:
            if cnt > 1:
                self.treeWidget.clear()
                self.lineDict.clear()
                self.gameDict.clear()
                self.headerDict.clear()
                if self.firstLoad:
                    bkpFile = os.path.join(self.amDir.text(), "romlists\\Mame.txt.bkp")
                    of = open(bkpFile, "w")

                fileToOpen = os.path.join(self.amDir.text(), "romlists\\Mame.txt")
                self.treeWidget.setSortingEnabled(False)
                with open(fileToOpen) as fp:
                    line = fp.readline()
                    if line:
                        self.fileHeader = line
                        headerlist = line.strip('# \n').split(';')
                        for i, header in enumerate(headerlist):
                            self.headerDict[header] = i
                    else:
                        return

                    line = fp.readline()
                    while line:
                        wordlist = line.strip('\n\r').split(';')
                        romname = wordlist[self.headerDict['Name']]
                        self.lineDict[romname] = line.strip('\n')
                        line = fp.readline()
                if self.firstLoad:
                    with open(bkpFile, "w") as of:
                        of.write(self.fileHeader)
                        for line in self.lineDict.values():
                            of.write(line+'\n')
                    of.close()
            self.loadTree()    

            app.processEvents()
            self.findDuplicates()

            self.treeWidget.setSortingEnabled(True)
            self.treeWidget.sortByColumn(0, Qt.AscendingOrder)
            self.treeWidget.sortByColumn(3, Qt.AscendingOrder)
            self.treeWidget.resizeColumnToContents(0)
            self.treeWidget.collapseAll()
            self.expColBtn.setText("Expand")
        except:
            traceback.print_exc()
            exit()

    def processRom(self, romname):
        ret = subprocess.run([self.mameExe.text(), romname, "-verifyroms", "-rompath", self.romPath], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
##        if ret.stdout != "":
##            linelist = list(enumerate(ret.stdout.split('\n')))
##        else:
##            linelist = list(enumerate(ret.stderr.split('\n')))
##        
##        for i, l in reversed(linelist):
##            wl = l.split(' ')
##            if wl[0] == "romset":
##                break
            
##        return ret.returncode, l
        return ret.returncode

##    def msgbtn(self, i):
##        print("Button pressed is {}".format(i.text()))
   
    def showErr(self, message):
        try:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)

            msg.setText(message)
#            msg.setInformativeText("This is additional information")
            msg.setWindowTitle("Error")
            msg.setStandardButtons(QMessageBox.Ok)
#            msg.buttonClicked.connect(self.msgbtn)
                
            retval = msg.exec_()
            return retval
        except:
            traceback.print_exc()

    def processList(self):
        pIdx = 0
        try:
            if not os.path.isfile(self.mameExe.text()):
                self.showErr('Invalid Mame executable, please fix and retry')
                return
            if os.path.isdir(self.amDir.text()):
                fileToOpen = os.path.join(self.amDir.text(), "emulators\\Mame.cfg")
                if not os.path.isfile(fileToOpen):
                    self.showErr('Unable to find {}, please fix and retry'.format(fileToOpen))
                    return
                self.romPath = self.getRomPath(fileToOpen)
            else:
                self.showErr('Invalid Attractmode directory, please fix and retry')
                return
            
            root = self.treeWidget.invisibleRootItem()
            titleCount = root.childCount()
            if titleCount == 0:
                self.showErr('No entries in list.  Please load Mame.txt before validating!')
                return
            d = QtWidgets.QDialog()
            self.treeWidget.expandAll()
            self.expColBtn.setText("Collapse")
            dui = ProgressDialog()
            dui.setupUi(d)
            d.show()
            romCount = 0
            for idx in range(titleCount):
                romCount += root.child(idx).childCount()
            dui.setProgressRange(1, romCount)
            for idx in range(titleCount):
                if dui.isCancelled() == True:
                    break;
                item = root.child(idx)
                for cIdx in range(item.childCount()):
                    pIdx += 1
                    child = item.child(cIdx)
                    romname = child.text(2)
##                    returncode, statusMsg = self.processRom(romname)
                    returncode = self.processRom(romname)                    
                    if returncode != 0:
                        child.setCheckState(0, Qt.Unchecked)
                        child.setText(4, 'fail')
                    else:
                        child.setText(4, 'pass')                        
                dui.setProgressValue(pIdx)
                self.ptxt.setText("{0} / {1}".format(pIdx, romCount))
                app.processEvents()
        except:
            traceback.print_exc()

    def findDuplicates(self):
        try:
            regFont = QFont()
            regFont.setBold(False)
            boldFont = QFont()
            boldFont.setBold(True)
            root = self.treeWidget.invisibleRootItem()
            titleCount = root.childCount()
            self.treeWidget.setSortingEnabled(False)
            for idx in range(titleCount):
                item = root.child(idx)
                if item.checkState(0) == QtCore.Qt.Unchecked:
                    item.setText(4, 'Excluded')
                else:
                    romname = ""
                    variation = ""
                    checkedCount = 0
                    for cIdx in range(item.childCount()):
                        child = item.child(cIdx)
                        if child.checkState(0) == QtCore.Qt.Checked:
                            if romname != "":
                                item.setFont(0, boldFont)
                                romname = ""
                                item.setText(4, 'Duplicates')
                                break
                            variation = child.text(1)
                            romname = child.text(2)
                    if romname != "":
                        item.setFont(0, regFont)
                        item.setText(1, variation)
                        item.setText(2, romname)
                        item.setText(4, 'Good')
            self.treeWidget.setSortingEnabled(True)
        except:
            traceback.print_exc()

    def unselectClones(self):
        try:
            root = self.treeWidget.invisibleRootItem()
            titleCount = root.childCount()
            for idx in range(titleCount):
                item = root.child(idx)
                if item.checkState(0) != QtCore.Qt.Unchecked:
                    parentRom = ""
                    for cIdx in range(item.childCount()):
                        child = item.child(cIdx)
                        if child.checkState(0) == QtCore.Qt.Checked:
                            if child.text(3) == "":
                                if parentRom == "":
                                    parentRom = child.text(2)
                                elif parentRom != child.text(2):
                                    parentRom = ""
                                    break
                    if parentRom != "":
                        for cIdx in range(item.childCount()):
                            child = item.child(cIdx)
                            if child.checkState(0) == QtCore.Qt.Checked and child.text(3) == parentRom and child.text(5) != 'Yes':
                                child.setCheckState(0, Qt.Unchecked)
            self.findDuplicates()
        except:
            traceback.print_exc()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
