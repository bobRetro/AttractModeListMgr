import sys 
import subprocess
import os.path
import json
import pickle

from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PyQt5.QtWidgets import *
from PyQt5.Qt import *

class amConfig:
    def __init__(self):    
        self.amDir = 'e:\\AttractMode'
        self.outFilePath = 'MameValidated.txt'
        self.mameExe = 'mame64.exe'
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    def loadJSON(self):
        with open('AttractModeListMgr.cfg', "r") as data_file:
            test = json.load(data_file)
            self.amDir = test["amDir"]
            self.outFilePath = test["outFilePath"]
            self.mameExe = test["mameExe"]
        
class Ui_Dialog(QWidget):
    fileHeader = str()
    lineDict = dict()
    configData = amConfig()
    outfilepath = 'e:\\AttractMode\\romlists\\MameValid.txt'
    configfile = 'AttractModeListMgr.cfg'

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(768, 406)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QtCore.QSize(768, 406))
        Dialog.setMaximumSize(QtCore.QSize(768, 406))
        self.amDir = QtWidgets.QLineEdit(Dialog)
        self.amDir.setGeometry(QtCore.QRect(160, 10, 261, 20))
        self.amDir.setObjectName("amDir")
        self.amDirLbl = QtWidgets.QLabel(Dialog)
        self.amDirLbl.setGeometry(QtCore.QRect(10, 10, 141, 16))
        self.amDirLbl.setObjectName("amDirLbl")
        self.progressBar = QtWidgets.QProgressBar(Dialog)
        self.progressBar.setGeometry(QtCore.QRect(20, 370, 671, 23))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.treeWidget = QtWidgets.QTreeWidget(Dialog)
        self.treeWidget.setGeometry(QtCore.QRect(20, 80, 731, 271))
        self.treeWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.treeWidget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.treeWidget.setColumnCount(4)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "1")
        self.treeWidget.headerItem().setText(1, "2")
        self.treeWidget.headerItem().setText(2, "3")
        self.treeWidget.headerItem().setText(3, "4")
        self.treeWidget.headerItem().setText(4, "5")
        self.amDirBtn = QtWidgets.QPushButton(Dialog)
        self.amDirBtn.setGeometry(QtCore.QRect(430, 10, 21, 21))
        self.amDirBtn.setObjectName("amDirBtn")
        self.startBtn = QtWidgets.QPushButton(Dialog)
        self.startBtn.setGeometry(QtCore.QRect(700, 370, 51, 25))
        self.startBtn.setObjectName("startBtn")
        self.ptxt = QtWidgets.QLabel(Dialog)
        self.ptxt.setGeometry(QtCore.QRect(20, 370, 631, 21))
        self.ptxt.setAlignment(QtCore.Qt.AlignCenter)
        self.ptxt.setObjectName("ptxt")
        self.mameExe = QtWidgets.QLineEdit(Dialog)
        self.mameExe.setGeometry(QtCore.QRect(160, 40, 261, 20))
        self.mameExe.setObjectName("mameExe")
        self.mameExeLbl = QtWidgets.QLabel(Dialog)
        self.mameExeLbl.setGeometry(QtCore.QRect(10, 40, 141, 16))
        self.mameExeLbl.setObjectName("mameExeLbl")
        self.mameExeBtn = QtWidgets.QPushButton(Dialog)
        self.mameExeBtn.setGeometry(QtCore.QRect(430, 40, 21, 21))
        self.mameExeBtn.setObjectName("mameExeBtn")
        self.loadListBtn = QtWidgets.QPushButton(Dialog)
        self.loadListBtn.setGeometry(QtCore.QRect(650, 10, 93, 21))
        self.loadListBtn.setObjectName("loadListBtn")
        self.saveConfigBtn = QtWidgets.QPushButton(Dialog)
        self.saveConfigBtn.setGeometry(QtCore.QRect(460, 10, 81, 21))
        self.saveConfigBtn.setObjectName("saveConfigBtn")
        self.saveMame2Btn = QtWidgets.QPushButton(Dialog)
        self.saveMame2Btn.setGeometry(QtCore.QRect(650, 40, 93, 21))
        self.saveMame2Btn.setObjectName("saveMame2Btn")
        
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
        self.saveMame2Btn.clicked.connect(self.saveMame2)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        if os.path.exists(self.configfile):
            self.configData.loadJSON()
            self.amDir.setText(self.configData.amDir)
            self.mameExe.setText(self.configData.mameExe)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.amDirLbl.setText(_translate("Dialog", "AttractMode Directory"))
        self.amDirBtn.setText(_translate("Dialog", "..."))
        self.startBtn.setText(_translate("Dialog", "Start"))
        self.ptxt.setText(_translate("Dialog", "TextLabel"))
        self.mameExeLbl.setText(_translate("Dialog", "Mame Executable"))
        self.mameExeBtn.setText(_translate("Dialog", "..."))
        self.loadListBtn.setText(_translate("Dialog", "Load Mame.txt"))
        self.saveConfigBtn.setText(_translate("Dialog", "Save Config"))
        self.saveMame2Btn.setText(_translate("Dialog", "Save Mame2.txt"))

    def saveConfig(self):
        self.configData.amDir = self.amDir.text()
        self.configData.mameExe = self.mameExe.text()
        with open(self.configfile, "w") as data_file:
            jsonString = self.configData.toJSON()
            linelist = jsonString.split('\n')
            for line in linelist:
                data_file.write(line+"\n")

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

    def saveMame2(self):
        root = self.treeWidget.invisibleRootItem()
        child_count = root.childCount()
        self.progressBar.setMaximum(child_count)
        fileToOpen = os.path.join(self.amDir.text(), "romlists\\Mame2.txt")
        of = open(fileToOpen, "w")

        of.write(self.fileHeader)
        for idx in range(child_count):
            item = root.child(idx)
            romname = item.text(2)
            if item.checkState(0) == QtCore.Qt.Checked:
                of.write(self.lineDict[romname])

        of.close()

    def getVariation(self, title):
        var = ''
        begIdx = -1
        endIdx = -1
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
                    break
        if begIdx > -1 and endIdx > -1:
            var = title[begIdx+1:endIdx]
        if begIdx > 0:
            newTitle = title[0:begIdx-1].strip()
        return var, newTitle;
            
    def loadList(self):
        idx = 0
        validCnt = 0
        cnt = self.getLineCount()
        self.progressBar.setMinimum(1)
        self.progressBar.setMaximum(100)
        if cnt > 1:
            self.treeWidget.clear()
            self.lineDict.clear()
            of = open(self.outfilepath, "w")
            fileToOpen = os.path.join(self.amDir.text(), "romlists\\Mame.txt")
            with open(fileToOpen) as fp:
                line = fp.readline()
                while line:
                    if idx == 0:
                        self.fileHeader = line
                    else:
                        wordlist = line.split(';')
                        romname = "{0}".format(wordlist[0].strip())
                        title = "{0}".format(wordlist[1].strip())

                        variation, newTitle = self.getVariation(title)
                        try:
                            self.lineDict[romname] = line
                        except:
                            print(sys.exc_info())
                        cloneOf = wordlist[3].strip()
                    
                        rowcount = self.treeWidget.topLevelItemCount()
                        try:
                            self.treeWidget.addTopLevelItem(QTreeWidgetItem(idx-1))
                            treeItem = self.treeWidget.topLevelItem(idx-1)
                            treeItem.setFlags(treeItem.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable)
                            treeItem.setText(0, newTitle)
                            treeItem.setText(1, variation)
                            treeItem.setText(2, romname)
                            treeItem.setText(3, cloneOf)
                            treeItem.setCheckState(0, Qt.Checked)
                        except:
                            print("Oops!", sys.exc_info()[0], "occurred.")

                    idx += 1
                        
                    self.ptxt.setText("{0} / {1}".format(idx, cnt))
                    self.progressBar.setValue(int(idx/cnt*100))
                    try:
                        app.processEvents()
                    except:
                        print("Oops!", sys.exc_info()[0], "occurred.")
                       
                    line = fp.readline()
                    if idx >= 20:
                        self.progressBar.setValue(100)
                        break
        self.treeWidget.setSortingEnabled(True)
        self.treeWidget.sortByColumn(3, Qt.AscendingOrder)
        self.treeWidget.sortByColumn(0, Qt.AscendingOrder)
        self.treeWidget.setSortingEnabled(False)


    def processList(self):
        root = self.treeWidget.invisibleRootItem()
        child_count = root.childCount()
        self.progressBar.setMaximum(child_count)
        for idx in range(child_count):
            item = root.child(idx)
            romname = item.text(2)
            try:
                ret = subprocess.run(["e:\\mame\\mame64", romname, "-verifyroms", "-rompath", "e:\\mame\\roms"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
                if ret.stdout != "":
                    linelist = list(enumerate(ret.stdout.split('\n')))
                else:
                    linelist = list(enumerate(ret.stderr.split('\n')))
                
                for i, l in reversed(linelist):
                    wl = l.split(' ')
                    if wl[0] == "romset":
                        item.setText(4, l)
                        lastLineIdx = i
                        break

                if ret.returncode != 0:
                    item.setCheckState(0, Qt.Unchecked)
##                    for i, w in linelist:
##                        if i == lastLineIdx:
##                            break
##                        msg = w.split(':')
##                        if len(msg) > 1:
##                            m = msg[1].strip()
##                        else:
##                            m = w.strip()
##                        childItem = QTreeWidgetItem()
##                        childItem.setText(3, m)
##                        item.insertChild(item.childCount(), childItem)
                self.progressBar.setValue(idx+1)
                app.processEvents()
            except:
                print("Oops!", sys.exc_info()[0], "occurred for {}.".format(romname))
                app.processEvents()
                
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())