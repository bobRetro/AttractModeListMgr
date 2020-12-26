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
        
class Ui_Dialog(object):
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
        self.treeWidget.headerItem().setText(0, "Rom")
        self.treeWidget.headerItem().setText(1, "Game")
        self.treeWidget.headerItem().setText(2, "CloneOf")
        self.treeWidget.headerItem().setText(3, "Status")
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
        self.loadListBtn.setGeometry(QtCore.QRect(470, 10, 93, 21))
        self.loadListBtn.setObjectName("loadListBtn")
        self.saveConfigBtn = QtWidgets.QPushButton(Dialog)
        self.saveConfigBtn.setGeometry(QtCore.QRect(570, 10, 93, 21))
        self.saveConfigBtn.setObjectName("saveConfigBtn")

        self.amDirBtn.clicked.connect(self.openAmDirDialog)
        self.startBtn.clicked.connect(self.processList2)
        self.loadListBtn.clicked.connect(self.loadList)
        self.saveConfigBtn.clicked.connect(self.saveConfig)

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

    def loadList(self):
        idx = 0
        validCnt = 0
        cnt = self.getLineCount()
        self.progressBar.setMinimum(1)
        self.progressBar.setMaximum(100)
        if cnt > 1:
            of = open(self.outfilepath, "w")
            fileToOpen = os.path.join(self.amDir.text(), "romlists\\Mame.txt")
            with open(fileToOpen) as fp:
                line = fp.readline()
                while line:
                    if idx > 0:
                        wordlist = line.split(';')
                        romname = "{0}".format(wordlist[0].strip())
                        title = "{0}".format(wordlist[1].strip())
                        cloneOf = wordlist[3].strip()
                    
                        rowcount = self.treeWidget.topLevelItemCount()
                        try:
                            self.treeWidget.addTopLevelItem(QTreeWidgetItem(idx-1))
                            treeItem = self.treeWidget.topLevelItem(idx-1)
                            treeItem.setFlags(treeItem.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable)
                            treeItem
                            treeItem.setText(0, romname)
                            treeItem.setText(1, title)
                            treeItem.setText(2, cloneOf)
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

    def processList2(self):
        root = self.treeWidget.invisibleRootItem()
        child_count = root.childCount()
        self.progressBar.setMaximum(child_count)
        for idx in range(child_count):
            item = root.child(idx)
            romname = item.text(0)
            try:
                ret = subprocess.run(["e:\\mame\\mame64", romname, "-verifyroms", "-rompath", "e:\\mame\\roms"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
                if ret.stdout != "":
                    linelist = list(enumerate(ret.stdout.split('\n')))
                else:
                    linelist = list(enumerate(ret.stderr.split('\n')))
                
                for i, l in reversed(linelist):
                    wl = l.split(' ')
                    if wl[0] == "romset":
                        item.setText(3, l)
                        lastLineIdx = i
                        break

                if ret.returncode != 0:
                    item.setCheckState(0, Qt.Unchecked)
                    for i, w in linelist:
                        if i == lastLineIdx:
                            break
                        msg = w.split(':')
                        if len(msg) > 1:
                            m = msg[1].strip()
                        else:
                            m = w.strip()
                        childItem = QTreeWidgetItem()
                        childItem.setText(3, m)
                        item.insertChild(item.childCount(), childItem)
                self.progressBar.setValue(idx+1)
                app.processEvents()
            except:
                print("Oops!", sys.exc_info()[0], "occurred for {}.".format(romname))
                app.processEvents()

    def processList(self):
        idx = 0
        validCnt = 0
        cnt = self.getLineCount()
        self.progressBar.setMinimum(1)
        self.progressBar.setMaximum(cnt)
        if cnt > 1:
            of = open(self.outfilepath, "w")
            fileToOpen = os.path.join(self.amDir.text(), "romlists\\Mame.txt")
            with open(fileToOpen) as fp:
                line = fp.readline()
                while line:
                    if idx > 0:
                        wordlist = line.split(';')
                        romname = "{0}".format(wordlist[0].strip())
                        title = "{0}".format(wordlist[1].strip())
                        cloneOf = wordlist[3].strip()
                        try:
                            ret = subprocess.run(["e:\\mame\\mame64", romname, "-verifyroms", "-rompath", "e:\\mame\\roms"], stdout=subprocess.PIPE, text=True, shell=True)
                            validCnt += 1
                            #print(ret)
                            if ret.returncode == 0:
                                of.write(line)
                                validCnt += 1
                        except:
                            print("Oops!", sys.exc_info()[0], "occurred.")
                    
                        rowcount = self.treeWidget.topLevelItemCount()
                        try:
                            self.treeWidget.addTopLevelItem(QTreeWidgetItem(idx-1))
                            self.treeWidget.topLevelItem(idx-1).setText(0, romname)
                            self.treeWidget.topLevelItem(idx-1).setText(1, title)
                            self.treeWidget.topLevelItem(idx-1).setText(2, cloneOf)
                            wordlist = ret.stdout.split('\n')
                            self.treeWidget.topLevelItem(idx-1).setText(3, wordlist[len(wordlist)-2])
                            tl = self.treeWidget.topLevelItem(idx-1)
                            if ret.returncode != 0:
                                i = 0
                                for w in wordlist:
                                    if i < len(wordlist)-2 and w != "":
                                        msg = w.split(':')
                                        childItem = QTreeWidgetItem()
                                        childItem.setText(3, msg[1].strip())
                                        tl.insertChild(tl.childCount(), childItem)
                                    i += 1
                        except:
                            print("Oops!", sys.exc_info()[0], "occurred.")

                    idx += 1
                        
                    self.ptxt.setText("{0} / {1}".format(idx, cnt))
                    try:
                        app.processEvents()
                    except:
                        print("Oops!", sys.exc_info()[0], "occurred.")
                       
                    self.progressBar.setValue(idx)                  
                    line = fp.readline()
                    if idx >= 100:
                        self.progressBar.setValue(100)
                        break
            of.close()
            fp.close()
                
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
