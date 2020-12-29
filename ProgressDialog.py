from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PyQt5.QtWidgets import *

class ProgressDialog(QWidget):
    cancelled = False
    def setupUi(self, Dialog):
        Dialog.setObjectName("ProgressDialog")
        Dialog.resize(450, 100)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QtCore.QSize(450, 100))
        Dialog.setMaximumSize(QtCore.QSize(450, 100))
        Dialog.setModal(True)
        self.progressBar = QtWidgets.QProgressBar(Dialog)
        self.progressBar.setGeometry(QtCore.QRect(30, 20, 401, 21))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.cancelBtn = QtWidgets.QPushButton(Dialog)
        self.cancelBtn.setGeometry(QtCore.QRect(200, 60, 75, 23))
        self.cancelBtn.setObjectName("cancelBtn")

        self.cancelBtn.clicked.connect(self.setCancelled)
        
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Progress"))
        self.cancelBtn.setText(_translate("Dialog", "Cancel"))

    def setProgressRange(self, min, max):
        self.progressBar.setMinimum(min)
        self.progressBar.setMaximum(max)

    def setProgressValue(self, val):
        self.progressBar.setValue(val)

    def setCancelled(self):
        self.cancelled = True
        self.close()
            
    def isCancelled(self):
        return self.cancelled

    def setButtonText(self, text):
        self.cancelBtn.setText(text)

