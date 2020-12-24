import sys 
import subprocess
import os.path

from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PyQt5.QtWidgets import *
from PyQt5.Qt import *


class Ui_Dialog(object):
    infilepath = 'e:\\AttractMode\\romlists\\Mame.txt'
    outfilepath = 'e:\\AttractMode\\romlists\\MameValid.txt'

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(768, 406)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.amDir = QtWidgets.QLineEdit(Dialog)
        self.amDir.setGeometry(QtCore.QRect(160, 40, 261, 20))
        self.amDir.setObjectName("amDir")
        self.amDirLbl = QtWidgets.QLabel(Dialog)
        self.amDirLbl.setGeometry(QtCore.QRect(10, 40, 141, 16))
        self.amDirLbl.setObjectName("amDirLbl")
        self.progressBar = QtWidgets.QProgressBar(Dialog)
        self.progressBar.setGeometry(QtCore.QRect(20, 370, 671, 23))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.treeWidget = QtWidgets.QTreeWidget(Dialog)
        self.treeWidget.setGeometry(QtCore.QRect(20, 80, 731, 271))
        self.treeWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.treeWidget.setColumnCount(3)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "Rom")
        self.treeWidget.headerItem().setText(1, "Game")
        self.treeWidget.headerItem().setText(2, "Status")
        self.amDirBtn = QtWidgets.QPushButton(Dialog)
        self.amDirBtn.setGeometry(QtCore.QRect(430, 40, 21, 21))
        self.amDirBtn.setObjectName("amDirBtn")
        self.startBtn = QtWidgets.QPushButton(Dialog)
        self.startBtn.setGeometry(QtCore.QRect(700, 370, 51, 25))
        self.startBtn.setObjectName("startBtn")
        self.ptxt = QtWidgets.QLabel(Dialog)
        self.ptxt.setGeometry(QtCore.QRect(20, 370, 631, 21))
        self.ptxt.setAlignment(QtCore.Qt.AlignCenter)
        self.ptxt.setObjectName("ptxt")

        self.amDirBtn.clicked.connect(self.openAmDirDialog)
        self.startBtn.clicked.connect(self.processList)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.amDirLbl.setText(_translate("Dialog", "AttractMode Directory"))
        self.amDirBtn.setText(_translate("Dialog", "..."))
        self.startBtn.setText(_translate("Dialog", "Start"))


    def getLineCount(self):
        lineCnt = 0
        fileToOpen = os.path.join(self.amDir.text(), "romlists\\Mame.txt")
        print(fileToOpen)
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
                            wordlist = ret.stdout.split('\n')
                            self.treeWidget.topLevelItem(idx-1).setText(2, wordlist[len(wordlist)-2])
                            tl = self.treeWidget.topLevelItem(idx-1)
                            if ret.returncode != 0:
                                i = 0
                                for w in wordlist:
                                    if i < len(wordlist)-2 and w != "":
                                        msg = w.split(':')
                                        childItem = QTreeWidgetItem()
                                        childItem.setText(2, msg[1].strip())
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
                    if idx >= 10:
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
