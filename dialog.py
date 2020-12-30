# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AttractModeMameListMgr.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
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

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "AttractMode Mame List Manager"))
        self.dupBtn.setText(_translate("Dialog", "Find Duplicates"))
        self.ptxt.setText(_translate("Dialog", "TextLabel"))
        self.treeWidget.setSortingEnabled(True)
        self.loadListBtn.setText(_translate("Dialog", "Load Mame.txt"))
        self.cloneBtn.setText(_translate("Dialog", "Unselect Clones"))
        self.expColBtn.setText(_translate("Dialog", "Expand"))
        self.amDirBtn.setText(_translate("Dialog", "..."))
        self.mameExeLbl.setText(_translate("Dialog", "Mame Executable"))
        self.saveConfigBtn.setText(_translate("Dialog", "Save Config"))
        self.amDirLbl.setText(_translate("Dialog", "AttractMode Directory"))
        self.mameExeBtn.setText(_translate("Dialog", "..."))
        self.saveMameBtn.setText(_translate("Dialog", "Save Mame.txt"))
        self.startBtn.setText(_translate("Dialog", "Validate"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
