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
        Dialog.resize(768, 406)
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
        self.gridLayout.addWidget(self.dupBtn, 3, 3, 1, 1)
        self.mameExe = QtWidgets.QLineEdit(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mameExe.sizePolicy().hasHeightForWidth())
        self.mameExe.setSizePolicy(sizePolicy)
        self.mameExe.setObjectName("mameExe")
        self.gridLayout.addWidget(self.mameExe, 1, 1, 1, 7)
        self.ptxt = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ptxt.sizePolicy().hasHeightForWidth())
        self.ptxt.setSizePolicy(sizePolicy)
        self.ptxt.setAlignment(QtCore.Qt.AlignCenter)
        self.ptxt.setObjectName("ptxt")
        self.gridLayout.addWidget(self.ptxt, 3, 10, 1, 1)
        self.treeWidget = QtWidgets.QTreeWidget(Dialog)
        self.treeWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.treeWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.treeWidget.setColumnCount(4)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "1")
        self.treeWidget.headerItem().setText(1, "2")
        self.treeWidget.headerItem().setText(2, "3")
        self.treeWidget.headerItem().setText(3, "4")
        self.gridLayout.addWidget(self.treeWidget, 2, 0, 1, 11)
        self.loadListBtn = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.loadListBtn.sizePolicy().hasHeightForWidth())
        self.loadListBtn.setSizePolicy(sizePolicy)
        self.loadListBtn.setObjectName("loadListBtn")
        self.gridLayout.addWidget(self.loadListBtn, 3, 0, 1, 1)
        self.cloneBtn = QtWidgets.QPushButton(Dialog)
        self.cloneBtn.setObjectName("cloneBtn")
        self.gridLayout.addWidget(self.cloneBtn, 3, 4, 1, 1)
        self.amDir = QtWidgets.QLineEdit(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.amDir.sizePolicy().hasHeightForWidth())
        self.amDir.setSizePolicy(sizePolicy)
        self.amDir.setObjectName("amDir")
        self.gridLayout.addWidget(self.amDir, 0, 1, 1, 7)
        self.expColBtn = QtWidgets.QPushButton(Dialog)
        self.expColBtn.setObjectName("expColBtn")
        self.gridLayout.addWidget(self.expColBtn, 1, 10, 1, 1)
        self.amDirBtn = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.amDirBtn.sizePolicy().hasHeightForWidth())
        self.amDirBtn.setSizePolicy(sizePolicy)
        self.amDirBtn.setMaximumSize(QtCore.QSize(25, 16777215))
        self.amDirBtn.setObjectName("amDirBtn")
        self.gridLayout.addWidget(self.amDirBtn, 0, 8, 1, 1)
        self.mameExeLbl = QtWidgets.QLabel(Dialog)
        self.mameExeLbl.setObjectName("mameExeLbl")
        self.gridLayout.addWidget(self.mameExeLbl, 1, 0, 1, 1)
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
        self.mameExeBtn = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mameExeBtn.sizePolicy().hasHeightForWidth())
        self.mameExeBtn.setSizePolicy(sizePolicy)
        self.mameExeBtn.setMaximumSize(QtCore.QSize(25, 16777215))
        self.mameExeBtn.setObjectName("mameExeBtn")
        self.gridLayout.addWidget(self.mameExeBtn, 1, 8, 1, 1)
        self.saveMameBtn = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.saveMameBtn.sizePolicy().hasHeightForWidth())
        self.saveMameBtn.setSizePolicy(sizePolicy)
        self.saveMameBtn.setObjectName("saveMameBtn")
        self.gridLayout.addWidget(self.saveMameBtn, 3, 1, 1, 1)
        self.startBtn = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.startBtn.sizePolicy().hasHeightForWidth())
        self.startBtn.setSizePolicy(sizePolicy)
        self.startBtn.setObjectName("startBtn")
        self.gridLayout.addWidget(self.startBtn, 3, 5, 1, 1)
        
        self.treeWidget.headerItem().setText(0, "Game")
        self.treeWidget.headerItem().setText(1, "Variation")
        self.treeWidget.headerItem().setText(2, "Rom")
        self.treeWidget.headerItem().setText(3, "CloneOf")
        self.treeWidget.headerItem().setText(4, "Status")
        
        self.amDirBtn.clicked.connect(self.openAmDirDialog)
        self.startBtn.clicked.connect(self.processList)
        self.loadListBtn.clicked.connect(self.loadList)
        self.saveConfigBtn.clicked.connect(self.saveConfig)
        self.mameExeBtn.clicked.connect(self.openMameExeDialog)
        self.saveMameBtn.clicked.connect(self.saveMame)
        self.dupBtn.clicked.connect(self.findDuplicates)
        self.cloneBtn.clicked.connect(self.unselectClones)
        self.expColBtn.clicked.connect(self.expColTree)
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
        self.amDirLbl.setText(_translate("Dialog", "AttractMode Directory"))        
        self.amDirBtn.setText(_translate("Dialog", "..."))
        self.startBtn.setText(_translate("Dialog", "Validate"))
        self.ptxt.setText(_translate("Dialog", "TextLabel"))
        self.mameExeLbl.setText(_translate("Dialog", "Mame Executable"))
        self.mameExeBtn.setText(_translate("Dialog", "..."))
        self.loadListBtn.setText(_translate("Dialog", "Load Mame.txt"))
        self.saveConfigBtn.setText(_translate("Dialog", "Save Config"))
        self.saveMameBtn.setText(_translate("Dialog", "Save Mame.txt"))
        self.dupBtn.setText(_translate("Dialog", "Find Duplicates"))
        self.cloneBtn.setText(_translate("Dialog", "Unselect Clones"))
        self.expColBtn.setText(_translate("Dialog", "Expand"))

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
            
    def setCheckedStatus(self, line, status):
        if status == '':
            newLine = line
        else:
            newLine = ""
            colList = line.split(';')
            for i,h in enumerate(self.headerDict):
                if h == 'Extra':
                    if status == 'included':
                        newLine = self.addDelimitedItem(newLine, 'included', ";")
                    else:
                        newLine = self.addDelimitedItem(newLine, 'excluded', ";")
                else:
                    newLine = self.addDelimitedItem(newLine, colList[i], ";")
        return newLine
            
    def saveMame(self):
        try:
            d = QtWidgets.QDialog()
            dui = ProgressDialog()
            dui.setupUi(d)
            d.show()
        except:
            traceback.print_exc()        
        try:
            root = self.treeWidget.invisibleRootItem()
            titleCount = root.childCount()
            romCount = 0
            for idx in range(titleCount):
                romCount += root.child(idx).childCount()            
            dui.setProgressRange(1, romCount)
            fileToOpen = os.path.join(self.amDir.text(), "romlists\\Mame.txt")
            of = open(fileToOpen, "w")

            of.write(self.fileHeader)
            pIdx = 0
            for idx in range(titleCount):
                item = root.child(idx)
                for cIdx in range(item.childCount()):
                    pIdx += 1
                    child = item.child(cIdx)
                    romname = child.text(2)
                    status = child.text(4)
                    newLine = self.setLineStatus(self.lineDict[romname], status)
                    if child.checkState(0) == QtCore.Qt.Checked:
                        newLine = self.setCheckedStatus(newLine, "included")
                    else:
                        newLine = self.setCheckedStatus(newLine, "excluded")
                    of.write(newLine+'\n')
                    dui.setProgressValue(pIdx)
                    self.ptxt.setText("{0} / {1}".format(pIdx, romCount))
                app.processEvents()
        except:
            traceback.print_exc()
        of.close()

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
            
    def loadList(self):
        try:
            d = QtWidgets.QDialog()
            dui = ProgressDialog()
            dui.setupUi(d)
            d.show()
            dui.setProgressRange(1, 100)
        except:
            traceback.print_exc()
        idx = 0
        validCnt = 0
        cnt = self.getLineCount()-1

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
                while line:
                    if dui.isCancelled() == True:
                        break;
                    if self.firstLoad:
                        of.write(line)
                    if idx == 0:
                        self.fileHeader = line
                        headerlist = line.strip('# \n').split(';')
                        for i, header in enumerate(headerlist):
                            self.headerDict[header] = i
                        romnameCol = self.headerDict['Name']
                        titleCol   = self.headerDict['Title']
                        cloneofCol = self.headerDict['CloneOf']
                        statusCol  = self.headerDict['Status']
                    else:
                        wordlist = line.strip('\n\r').split(';')
                        romname = wordlist[romnameCol]
                        title   = wordlist[titleCol]
                        cloneOf = wordlist[cloneofCol]
                        status  = wordlist[statusCol]
                        statusList = status.split(',')
                        status = ''
                        for s in statusList:
                            if s == 'pass' or s == 'fail':
                                status = s
                                
                        variation, newTitle = self.getVariation(title)
                        try:
                            self.lineDict[romname] = line.strip('\n')
                        except:
                            print(sys.exc_info())

                        if newTitle not in self.gameDict.keys():
                            try:
                                gameIdx = self.treeWidget.topLevelItemCount()
                                self.gameDict[newTitle] = gameIdx
                                self.treeWidget.addTopLevelItem(QTreeWidgetItem(gameIdx))
                                treeItem = self.treeWidget.topLevelItem(gameIdx)
                                treeItem.setFlags(treeItem.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsTristate)
                                treeItem.setText(0, newTitle)
##                                brush_yellow=QBrush(Qt.yellow)
##                                treeItem.setBackground(0,brush_yellow)
                            except:
                                traceback.print_exc()
                        else:
                            gameIdx = self.gameDict[newTitle]
                            treeItem = self.treeWidget.topLevelItem(gameIdx)
                        
                        childItem = QTreeWidgetItem()
                        extra = wordlist[self.headerDict['Extra']]
                        extraList = extra.split(',')
                        try:
                            checked = ''
                            for c in extraList:
                                if c == 'included' or c == 'excluded':
                                    checked = c
                            if checked == 'excluded':
                                childItem.setCheckState(0, Qt.Unchecked)
                            else:
                                childItem.setCheckState(0, Qt.Checked)
                        except:
                            traceback.print_exc()
                            exit
                        childItem.setText(0, newTitle)
                        childItem.setText(1, variation)
                        childItem.setText(2, romname)
                        childItem.setText(3, cloneOf)
                        childItem.setText(4, status)
                        treeItem.insertChild(treeItem.childCount(), childItem)
                        
                    idx += 1
                        
                    self.ptxt.setText("{0} / {1}".format(idx-1, cnt))
                    dui.setProgressValue(int(idx/cnt*100))
                    try:
                        if idx%100 == 0 or idx == cnt:
                            app.processEvents()
                    except:
                        print("Oops!", sys.exc_info()[0], "occurred.")
                       
                    line = fp.readline()
                if self.firstLoad:
                    of.close()
                if dui.isCancelled() == False:
                    self.firstLoad = False
                    self.findDuplicates()

        self.treeWidget.setSortingEnabled(True)
        self.treeWidget.sortByColumn(3, Qt.AscendingOrder)
        self.treeWidget.sortByColumn(0, Qt.AscendingOrder)
        self.treeWidget.resizeColumnToContents(0)
        self.treeWidget.collapseAll()
        self.expColBtn.setText("Expand")
        try:
            dui.setButtonText('OK')
        except:
            traceback.print_exc()
#        d.exec_()

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
                            if child.checkState(0) == QtCore.Qt.Checked and child.text(3) == parentRom:
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
