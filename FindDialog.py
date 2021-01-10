import traceback

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QDialog


class Ui_findDlg(object):
    def __init__(self, parent=None):
        self.parent = parent

    def setupUi(self, findDlg):

        findDlg.setObjectName("findDlg")
        findDlg.resize(400, 135)
        findDlg.setModal(True)
        self.buttonBox = QtWidgets.QDialogButtonBox(findDlg)
        self.buttonBox.setGeometry(QtCore.QRect(310, 100, 71, 30))
        self.buttonBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel)
        self.buttonBox.setObjectName("buttonBox")
        self.findLine = QtWidgets.QLineEdit(findDlg)
        self.findLine.setGeometry(QtCore.QRect(50, 10, 241, 20))
        self.findLine.setObjectName("findLine")
        self.findLbl = QtWidgets.QLabel(findDlg)
        self.findLbl.setGeometry(QtCore.QRect(10, 10, 47, 13))
        self.findLbl.setObjectName("findLbl")
        self.findBtn = QtWidgets.QPushButton(findDlg)
        self.findBtn.setGeometry(QtCore.QRect(310, 10, 71, 30))
        self.findBtn.setObjectName("findBtn")
        self.cbxGroups = QtWidgets.QCheckBox(findDlg)
        self.cbxGroups.setGeometry(QtCore.QRect(50, 80, 74, 17))
        self.cbxGroups.setObjectName("cbxGroups")
        self.cbxChildren = QtWidgets.QCheckBox(findDlg)
        self.cbxChildren.setGeometry(QtCore.QRect(50, 100, 74, 17))
        self.cbxChildren.setObjectName("cbxChildren")
        self.cbxInclSiblings = QtWidgets.QCheckBox(findDlg)
        self.cbxInclSiblings.setGeometry(QtCore.QRect(150, 40, 141, 17))
        self.cbxInclSiblings.setObjectName("cbxInclSiblings")
        self.cbxExactMatch = QtWidgets.QCheckBox(findDlg)
        self.cbxExactMatch.setGeometry(QtCore.QRect(50, 40, 91, 17))
        self.cbxExactMatch.setObjectName("cbxExactMatch")
        self.duplicatesBtn = QtWidgets.QPushButton(findDlg)
        self.duplicatesBtn.setGeometry(QtCore.QRect(310, 50, 71, 28))
        self.duplicatesBtn.setObjectName("DuplicatesBtn")

        self.cbxChildren.setChecked(True)
        self.cbxGroups.setChecked(True)

        self.retranslateUi(findDlg)
        self.buttonBox.accepted.connect(findDlg.accept)
        self.buttonBox.rejected.connect(findDlg.reject)
        self.findBtn.clicked.connect(self.doSearch)
        self.findLine.textEdited.connect(self.findLineClicked)
        self.duplicatesBtn.clicked.connect(self.findDuplicates)
        QtCore.QMetaObject.connectSlotsByName(findDlg)

    def retranslateUi(self, findDlg):
        _translate = QtCore.QCoreApplication.translate
        findDlg.setWindowTitle(_translate("findDlg", "Find"))
        self.findLbl.setText(_translate("findDlg", "Find"))
        self.findBtn.setText(_translate("findDlg", "Search"))
        self.cbxGroups.setText(_translate("findDlg", "Groups"))
        self.cbxChildren.setText(_translate("findDlg", "Children"))
        self.cbxInclSiblings.setText(_translate("findDlg", "Include siblings in results"))
        self.cbxExactMatch.setText(_translate("findDlg", "Exact Match"))
        self.duplicatesBtn.setText(_translate("findDlg", "Duplicates"))

    def findLineClicked(self):
        self.findBtn.setDefault(True)
        self.findBtn.setAutoDefault(True)

    def doSearch(self):
        try:
            self.parent.searchList(self.findLine.text())
        except Exception as e:
            traceback.print_exc()
            raise e

    def findDuplicates(self):
        self.parent.findDuplicates()
