import traceback
import subprocess
import os.path

from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PyQt5.Qt import *
from ProgressDialog import ProgressDialog
from ConfigDialog import Ui_configDialog
from AmConfig import AmConfig
from FindDialog import Ui_findDlg


def getConfigLevel(line):
    i = 0
    while line[i] == '\t':
        i += 1
    return i


def getCfgLineKeyVal(line):
    level = getConfigLevel(line)
    keyVal = ' '.join(line.strip().split()).split(' ')
    if len(keyVal) >= 2:
        return level, keyVal[0], ' '.join(keyVal[1:])
    else:
        return 0, None, None


def getRomPath(fileToOpen):
    if os.path.isfile(fileToOpen):
        romPath = ""
        with open(fileToOpen, "r") as fp:
            line = fp.readline()
            while line:
                lvl, key, val = getCfgLineKeyVal(line)
                if key == 'rompath':
                    romPath = val
                    break
                line = fp.readline()
        return romPath
    else:
        return "Invalid Path"


def showErr(message):
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
    except Exception as e:
        traceback.print_exc()
        raise e


def getStatus(status):
    statusList = status.split(',')
    status = ''
    for s in statusList:
        if s == 'pass' or s == 'fail':
            status = s
    return status


def loadDisplayCfg(cfgList, listIdx):
    cfgDict = dict()
    cfgDict['filter'] = dict()
    filterName = ''
    for i in range(listIdx+1, len(cfgList)):
        line = cfgList[i]
        lvl, cfgKey, cfgVal = getCfgLineKeyVal(line)
        if lvl == 1:
            if cfgKey == 'filter':
                filterName = cfgVal
                cfgDict['filter'][filterName] = list()
            else:
                cfgDict[cfgKey] = cfgVal
        elif lvl == 2 and cfgKey == 'rule':
            cfgDict['filter'][filterName].append(cfgVal)
        elif lvl == 0:
            return cfgDict, i

    return cfgDict, len(cfgList)


def loadAmConfig(fileToOpen):
    dispDict = dict()
    if os.path.exists(fileToOpen):
        cfgList = list()
    #    fileToOpen = 'e:\\AttractMode\\attract.cfg'
        with open(fileToOpen, "r") as amConfig:
            line = amConfig.readline()
            while line:
                cfgList.append(line)
                line = amConfig.readline()
        for i, line in enumerate(cfgList):
            lvl, dispKey, dispVal = getCfgLineKeyVal(line)
            if lvl == 0 and dispKey == 'display':
                dispDict[dispVal], i = loadDisplayCfg(cfgList, i)
    return dispDict

def getTitleVariation(title):
    try:
        var = ''
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
                    if var != "":
                        var = ' - ' + var.strip()
                    var = title[i+1:endIdx] + var
                    newBegIdx = i
                    endIdx = -1
        if newBegIdx > 0:
            newTitle = title[0:newBegIdx-1].strip()
    except Exception as e:
        traceback.print_exc()
        raise e
    return newTitle, var


def addDelimitedItem(line, value, delimiter):
    newLine = line
    if newLine != "":
        newLine += delimiter
    newLine += value
    return newLine


def removeFieldVal(field, val):
    if val == '':
        return field
    newField = ""
    valList = field.split(',')
    for j in valList:
        if j != val:
            newField = addDelimitedItem(newField, j, ",")
    return newField


def addFieldVal(field, val):
    if val == '':
        return field
    newField = field
    valList = field.split(',')
    for j in valList:
        if j == val:
            return newField
    newField = addDelimitedItem(newField, val, ",")
    return newField


class Ui_MainWindow(QMainWindow):
    dataChanged = False
    fileHeader = str()
    lineDict = dict()
    headerDict = dict()
    gameDict = dict()
    titleDict = dict()
    dispDict = dict()
    romlistDict = dict()
    emuDict = dict()
    favList = list()
    configData = AmConfig()
    configfile = 'AttractModeMameListMgr.cfg'
    groupMode = 'parent'
    romPath = ""
    firstLoad = True
    treeLoading = False
    listName = "Mame"

    def _windowLayout(self):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(906, 525)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.cloneBtn = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cloneBtn.sizePolicy().hasHeightForWidth())
        self.cloneBtn.setSizePolicy(sizePolicy)
        self.cloneBtn.setObjectName("cloneBtn")
        self.gridLayout.addWidget(self.cloneBtn, 1, 4, 1, 1)
        self.frame = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QtCore.QSize(250, 30))
        self.frame.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.frame.setFrameShape(QtWidgets.QFrame.Panel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame.setLineWidth(1)
        self.frame.setMidLineWidth(1)
        self.frame.setObjectName("frame")
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(10, 0, 58, 28))
        self.label.setObjectName("label")
        self.parentBtn = QtWidgets.QRadioButton(self.frame)
        self.parentBtn.setGeometry(QtCore.QRect(100, 6, 56, 17))
        self.parentBtn.setObjectName("parentBtn")
        self.titleBtn = QtWidgets.QRadioButton(self.frame)
        self.titleBtn.setGeometry(QtCore.QRect(180, 6, 44, 17))
        self.titleBtn.setObjectName("titleBtn")
        self.gridLayout.addWidget(self.frame, 0, 1, 2, 2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 8, 1, 1)
        self.startBtn = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.startBtn.sizePolicy().hasHeightForWidth())
        self.startBtn.setSizePolicy(sizePolicy)
        self.startBtn.setObjectName("startBtn")
        self.gridLayout.addWidget(self.startBtn, 1, 9, 1, 1)
        self.treeWidget = QtWidgets.QTreeWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.treeWidget.sizePolicy().hasHeightForWidth())
        self.treeWidget.setSizePolicy(sizePolicy)
        self.treeWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.treeWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.treeWidget.setColumnCount(4)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "1")
        self.treeWidget.headerItem().setText(1, "2")
        self.treeWidget.headerItem().setText(2, "3")
        self.treeWidget.headerItem().setText(3, "4")
        self.treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeWidget.customContextMenuRequested.connect(self.menuContextTree)

        self.gridLayout.addWidget(self.treeWidget, 3, 0, 1, 10)
        self.clearSearchBtn = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.clearSearchBtn.sizePolicy().hasHeightForWidth())
        self.clearSearchBtn.setSizePolicy(sizePolicy)
        self.clearSearchBtn.setObjectName("clearSearchBtn")
        self.gridLayout.addWidget(self.clearSearchBtn, 1, 6, 1, 1)
        self.expColBtn = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.expColBtn.sizePolicy().hasHeightForWidth())
        self.expColBtn.setSizePolicy(sizePolicy)
        self.expColBtn.setObjectName("expColBtn")
        self.gridLayout.addWidget(self.expColBtn, 1, 3, 1, 1)
        self.failedBtn = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.failedBtn.sizePolicy().hasHeightForWidth())
        self.failedBtn.setSizePolicy(sizePolicy)
        self.failedBtn.setObjectName("failedBtn")
        self.gridLayout.addWidget(self.failedBtn, 1, 7, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 906, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.lockIcon = QtGui.QIcon("lock.ico")
        self.findDlg = QtWidgets.QDialog()
        self.findUi = Ui_findDlg(parent=self)
        self.findUi.setupUi(self.findDlg)

        self.configDialog = QtWidgets.QDialog()
        self.configUi = Ui_configDialog(parent=self)
        self.configUi.setupUi(self.configDialog)

    def setupUi(self, myMainWindow):
        self._windowLayout()
        
        self.treeWidget.headerItem().setText(0, "Game")
        self.treeWidget.headerItem().setText(1, "Variation")
        self.treeWidget.headerItem().setText(2, "Rom")
        self.treeWidget.headerItem().setText(3, "CloneOf")
        self.treeWidget.headerItem().setText(4, "Status")
        self.treeWidget.headerItem().setText(5, "Emulator")
        self.treeWidget.headerItem().setText(6, "Favorite")
        self.treeWidget.headerItem().setText(7, "Category")
        
        self.startBtn.clicked.connect(self.processList)
        self.cloneBtn.clicked.connect(self.unselectClones)
        self.expColBtn.clicked.connect(self.expColTree)
        self.parentBtn.setChecked(True)
        self.groupMode = 'parent'
        self.parentBtn.toggled.connect(self.toggleMode)
        self.titleBtn.toggled.connect(self.toggleMode)
        self.clearSearchBtn.clicked.connect(self.clearSearch)
        self.failedBtn.clicked.connect(self.toggleFailed)

        self.treeWidget.itemChanged[QTreeWidgetItem, int].connect(self.treeItemChanged)
#        self.treeWidget.itemSelectionChanged.connect(self.treeItemSelected)
        
        menubar = self.menuBar()
        style = self.style()
        icon = QtGui.QIcon(style.standardIcon(getattr(QStyle, 'SP_BrowserStop')))
        exitAct = QAction(icon, 'Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.closeProgram)

        icon = QtGui.QIcon(style.standardIcon(getattr(QStyle, 'SP_DialogOpenButton')))
        loadAct = QAction(icon, 'Load', self)
        loadAct.setShortcut('Ctrl+L')
        loadAct.setStatusTip('Load File')
        loadAct.triggered.connect(lambda: self.loadList('Mame'))

        icon = QtGui.QIcon(style.standardIcon(getattr(QStyle, 'SP_DialogSaveButton')))
        
        self.saveAct = QAction(icon, 'Save', self)
        self.saveAct.setShortcut('Ctrl+S')
        self.saveAct.setStatusTip('Save File')
        self.saveAct.triggered.connect(self.saveMame)
        self.saveAct.setEnabled(False)

        findAct = QAction(icon, 'Find', self)
        findAct.setShortcut('Ctrl+F')
        findAct.setStatusTip('Find')
        findAct.triggered.connect(self.showFindDlg)

        configAct = QAction(icon, 'Preferences', self)
        configAct.setShortcut('Ctrl+P')
        configAct.setStatusTip('Set Preferences')
        configAct.triggered.connect(self.showPreferences)

        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(loadAct)
        fileMenu.addAction(self.saveAct)
        fileMenu.addAction(findAct)
        fileMenu.addAction(configAct)
        fileMenu.addAction(exitAct)

        fileMenu.aboutToShow.connect(self.populateFileMenu)

        self.treeWidget.setSortingEnabled(True)

        self.retranslateUi(MainWindow)

        MainWindow.setWindowFlags(myMainWindow.windowFlags() |
                                  QtCore.Qt.WindowMinimizeButtonHint |
                                  QtCore.Qt.WindowMaximizeButtonHint)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.loadAmConfigFile()

    def menuContextTree(self, point):
        try:
            index = self.treeWidget.indexAt(point)

            if not index.isValid():
                return

            item = self.treeWidget.itemAt(point)
            name = item.text(0)  # The text of the node.

            # We build the menu.
            menu = QtWidgets.QMenu()
            self.setLockContextMenu(menu, point)
#            action = menu.addAction(name)
            menu.addSeparator()
            self.setCheckedContextMenu(menu, point)
            action_1 = menu.addAction("Choix 1")
            action_2 = menu.addAction("Choix 2")
            action_3 = menu.addAction("Choix 3")


            menu.exec_(self.treeWidget.mapToGlobal(point))
        except Exception as e:
            traceback.print_exc()
            raise e

    def addMenu(self, menuName, subMenuDict, connectAction):
        dispMenu = None
        for d in self.menuBar().children():
            if isinstance(d, QMenu) and d.title() == menuName:
                dispMenu = d
                break
        if not isinstance(dispMenu, QMenu):
            dispMenu = self.menuBar().addMenu(menuName)
        else:
            print("Found Display")
        for a in dispMenu.actions():
            dispMenu.removeAction(a)
            print('Remove {}'.format(a.text()))
        for d in subMenuDict.keys():
            dispAct = QAction(d, self)
            dispAct.triggered.connect(connectAction)
            print("Rom List for {} is {}".format(d, self.dispDict[d]['romlist']))

            dispMenu.addAction(dispAct)

    def loadAmConfigFile(self):
        if os.path.exists(self.configfile):
            self.configData.loadJSON(self.configfile)
            self.configUi.amDir.setText(self.configData.amDir)
            self.configUi.mameExe.setText(self.configData.mameExe)
            self.dispDict = loadAmConfig(os.path.join(self.configData.amDir, "attract.cfg"))

            self.addMenu('Display', self.dispDict, self.loadDisp)

    def showPreferences(self):
        try:
            currAmDir = self.configUi.amDir.text()
            currMameExe = self.configUi.mameExe.text()

            self.configDialog.show()
            rsp = self.configDialog.exec_()
            if rsp == QDialog.Accepted:
                if self.configData.amDir != self.configUi.amDir.text():
                    loadConfig = True
                else:
                    loadConfig = False
                if (self.configData.amDir != self.configUi.amDir.text() or
                        self.configData.mameExe != self.configUi.mameExe.text()):
                    self.configData.amDir = self.configUi.amDir.text()
                    self.configData.mameExe = self.configUi.mameExe.text()
                    self.configData.saveJSON(self.configfile)
                if loadConfig:
                    self.loadAmConfigFile()
            else:
                self.configUi.amDir.setText(currAmDir)
                self.configUi.mameExe.setText(currMameExe)
        except Exception as e:
            traceback.print_exc()
            raise e

    def ignoreUnsavedChangesWarning(self):
        if self.dataChanged:
            reply = QMessageBox.question(self,
                                         "Unsaved Changes",
                                         "There are unsaved changes. Are you sure you want to exit?",
                                         QMessageBox.Yes,
                                         QMessageBox.No)
            if reply == QMessageBox.Yes:
                return True
            else:
                return False
        else:
            return True

    def loadDisp(self):
        try:
            if self.ignoreUnsavedChangesWarning():
                self.dataChanged = False
                self.saveAct.setEnabled(False)
                action = self.sender()
                self.loadList(action.text())
        except Exception as e:
            traceback.print_exc()
            raise e

    def closeProgram(self):
        self.close()

    def closeEvent(self, event):
        try:
            if self.ignoreUnsavedChangesWarning():
                event.accept()
            else:
                event.ignore()
        except Exception as e:
            traceback.print_exc()
            raise e

    def showFindDlg(self):
        self.findDlg.show()
        self.findUi.findLineClicked()
        self.findUi.findBtn.setAutoDefault(True)
        self.findUi.findLine.setFocus()
        
#    def keyPressEvent(self, e):
#        if e.key() == Qt.Key_Escape:
#            self.close()
    
    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.cloneBtn.setText(_translate("MainWindow", "Unselect Clones"))
        self.label.setText(_translate("MainWindow", "Group Mode"))
        self.parentBtn.setText(_translate("MainWindow", "Parent"))
        self.titleBtn.setText(_translate("MainWindow", "Title"))
        self.startBtn.setText(_translate("MainWindow", "Validate"))
        self.treeWidget.setSortingEnabled(True)
        self.clearSearchBtn.setText(_translate("MainWindow", "Clear Search"))
        self.expColBtn.setText(_translate("MainWindow", "Expand"))
        self.failedBtn.setText(_translate("MainWindow", "Hide Failed"))

    def populateFileMenu(self):
        try:
            if self.dataChanged:
                self.saveAct.setEnabled(True)
        except Exception as e:
            traceback.print_exc()
            raise e

    # def treeItemSelected(self):
    #     try:
    #         for i in self.treeWidget.selectedItems():
    #             if i.parent():
    #                 self.lockBtn.setEnabled(True)
    #                 line = self.lineDict[i.text(2)]
    #                 extra = self.getField(line, 'Extra')
    #                 if 'locked' in extra.split(','):
    #                     self.lockBtn.setText('Unlock Selected')
    #                 else:
    #                     self.lockBtn.setText('Lock Selected')
    #             else:
    #                 self.lockBtn.setEnabled(False)
    #     except Exception as e:
    #         traceback.print_exc()
    #         raise e

    def treeItemChanged(self, item, column):
        if not self.treeLoading:
            self.dataChanged = True
#            if item.checkState(column) == Qt.Checked:
#                print(f'{item.text(column)} was checked')

    def toggleMode(self):
        radioButton = self.sender()
        if radioButton.isChecked():
            if radioButton.objectName() == 'parentBtn':
                self.groupMode = 'parent'
            elif radioButton.objectName() == 'titleBtn':
                self.groupMode = 'title'
            self.updateLineDict()
            self.loadTree(self.groupMode)
            
    def searchLineClicked(self):
        self.searchBtn.setDefault(True)
        self.searchBtn.setAutoDefault(True)

    def getSelectedExtraFieldCount(self, extra_field):
        item_count = 0
        field_count = 0
        selected_items = self.treeWidget.selectedItems()
        for tree_item in selected_items:
            if tree_item.parent():
                item_count += 1
                newLine = self.lineDict[tree_item.text(2)]
                extra = self.getField(newLine, 'Extra')
                if extra_field in extra.split(','):
                    field_count += 1
        return item_count, field_count

    def setLockContextMenu(self, menu, point):
        name = ""
        item_count, locked_count = self.getSelectedExtraFieldCount('locked')

        if item_count > 0:
            if item_count == 1:
                name = " "+self.treeWidget.itemAt(point).text(0)

            if locked_count == item_count:
                action = menu.addAction("Unlock"+name)
                action.triggered.connect(self.unlockSelected)
            elif locked_count == 0:
                action = menu.addAction("Lock"+name)
                action.triggered.connect(self.lockSelected)
            else:
                action = menu.addAction("Toggle Lock")
                action.triggered.connect(self.toggleLockSelected)
                action = menu.addAction("Unlock")
                action.triggered.connect(self.unlockSelected)
                action = menu.addAction("Lock")
                action.triggered.connect(self.lockSelected)

    def lockItem(self, tree_item):
        if tree_item.parent():
            newLine = self.lineDict[tree_item.text(2)]
            tree_item.setIcon(0, self.lockIcon)
            self.lineDict[tree_item.text(2)] = self.setFieldVal(newLine, 'Extra', 'locked', '')

    def unlockItem(self, tree_item):
        if tree_item.parent():
            newLine = self.lineDict[tree_item.text(2)]
            icon = QtGui.QIcon()
            tree_item.setIcon(0, icon)
            self.lineDict[tree_item.text(2)] = self.setFieldVal(newLine, 'Extra', '', 'locked')

    def unlockSelected(self):
        selected_items = self.treeWidget.selectedItems()
        for tree_item in selected_items:
            self.unlockItem(tree_item)

    def lockSelected(self):
        selected_items = self.treeWidget.selectedItems()
        for tree_item in selected_items:
            self.lockItem(tree_item)

    def toggleLockSelected(self):
        selected_items = self.treeWidget.selectedItems()
        for tree_item in selected_items:
            if tree_item.parent():
                newLine = self.lineDict[tree_item.text(2)]
                extra = self.getField(newLine, 'Extra')
                if 'locked' in extra.split(','):
                    self.unlockItem(tree_item)
                else:
                    self.lockItem(tree_item)

    def checkItem(self, tree_item):
        if tree_item.parent():
            newLine = self.lineDict[tree_item.text(2)]
            self.lineDict[tree_item.text(2)] = self.setFieldVal(newLine, 'Extra', '', 'excluded')
            tree_item.setCheckState(0, Qt.Checked)

    def uncheckItem(self, tree_item):
        if tree_item.parent():
            newLine = self.lineDict[tree_item.text(2)]
            self.lineDict[tree_item.text(2)] = self.setFieldVal(newLine, 'Extra', 'excluded', '')
            tree_item.setCheckState(0, Qt.Unchecked)

    def uncheckSelected(self):
        selected_items = self.treeWidget.selectedItems()
        for tree_item in selected_items:
            self.uncheckItem(tree_item)

    def checkSelected(self):
        selected_items = self.treeWidget.selectedItems()
        for tree_item in selected_items:
            self.checkItem(tree_item)

    def toggleCheckSelected(self):
        selected_items = self.treeWidget.selectedItems()
        for tree_item in selected_items:
            if tree_item.parent():
                newLine = self.lineDict[tree_item.text(2)]
                extra = self.getField(newLine, 'Extra')
                if 'excluded' in extra.split(','):
                    self.checkItem(tree_item)
                else:
                    self.uncheckItem(tree_item)

    def setCheckedContextMenu(self, menu, point):
        name = ""
        item_count, unchecked_count = self.getSelectedExtraFieldCount('excluded')

        if item_count > 0:
            if item_count == 1:
                name = " "+self.treeWidget.itemAt(point).text(0)

            if unchecked_count == item_count:
                action = menu.addAction("Check"+name)
                action.triggered.connect(self.checkSelected)
            elif unchecked_count == 0:
                action = menu.addAction("Uncheck"+name)
                action.triggered.connect(self.uncheckSelected)
            else:
                action = menu.addAction("Toggle checked")
                action.triggered.connect(self.toggleCheckSelected)
                action = menu.addAction("Uncheck")
                action.triggered.connect(self.uncheckSelected)
                action = menu.addAction("Check")
                action.triggered.connect(self.checkSelected)

    def setTreeHidden(self, hidden):
        root = self.treeWidget.invisibleRootItem()
        titleCount = root.childCount()
        for idx in range(titleCount):
            item = root.child(idx)
            item.setHidden(hidden)
            for cIdx in range(item.childCount()):
                child = item.child(cIdx)
                child.setHidden(hidden)
        
    def searchList(self, searchTerm):
        if searchTerm != "":
            self.setTreeHidden(True)

            if self.findUi.cbxExactMatch.isChecked():
                searchFlags = QtCore.Qt.MatchExactly
            else:
                searchFlags = QtCore.Qt.MatchContains

            if self.findUi.cbxChildren.isChecked():
                searchFlags |= QtCore.Qt.MatchRecursive

            resultItems = self.treeWidget.findItems(searchTerm, searchFlags, 0)
            for item in resultItems:
                if self.failedBtn.text() == 'Hide Failed' or self.failedBtn.text() == 'Show Failed' and item.text(4) != 'fail':
                    item.setHidden(False)
                    if item.parent():
                        item.parent().setHidden(False)
                        if self.findUi.cbxInclSiblings.isChecked():
                            for cIdx in range(item.parent().childCount()):
                                item.parent().child(cIdx).setHidden(False)

    def expColTree(self):
        try:
            if self.expColBtn.text() == "Expand":
                self.treeWidget.expandAll()
                self.expColBtn.setText("Collapse")
            else:
                self.treeWidget.collapseAll()
                self.expColBtn.setText("Expand")
        except Exception as e:
            traceback.print_exc()
            raise e
            
    def getLineCount(self):
        lineCnt = 0
        fileToOpen = os.path.join(self.configData.amDir, "romlists\\Mame.txt")
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
            if fileName:
                self.amDir.setText(os.path.normpath(fileName))
        except Exception as e:
            print("Oops!", sys.exc_info()[0], "occurred.")
            raise e

    def openMameExeDialog(self):
        try:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            dirName = os.path.dirname(os.path.realpath(self.configData.mameExe))
            if os.path.isdir(dirName):
                tempDir = dirName
            else:
                tempDir = 'c:\\'
            fileName, _ = QFileDialog.getOpenFileName(self, 'Mame Exe', tempDir, "Exe files (*.exe)")
            if os.path.isfile(fileName):
                self.mameExe.setText(os.path.normpath(fileName))
        except Exception as e:
            print("Oops!", sys.exc_info()[0], "occurred.")
            raise e

    def setLineStatus(self, line, status):
        if status == '':
            newLine = line
        else:
            newLine = ""
            colList = line.split(';')
            for i, h in enumerate(self.headerDict):
                if h == 'Status':
                    statusList = colList[i].split(',')
                    newStatus = ""
                    for s in statusList:
                        if s != 'pass' and s != 'fail':
                            newStatus = addDelimitedItem(newStatus, s, ",")
                    newStatus = addDelimitedItem(newStatus, status, ",")
                    newLine = addDelimitedItem(newLine, newStatus, ";")
                else:
                    newLine = addDelimitedItem(newLine, colList[i], ";")
        return newLine

    def getField(self, line, field):
        if field in self.headerDict.keys():
            return line.split(';')[self.headerDict[field]]
        else:
            return None

    def setFieldVal(self, line, field, addVal, remVal):
        newLine = ""
        colList = line.split(';')
        for i, h in enumerate(self.headerDict):
            newField = colList[i]
            if h == field:
                newField = removeFieldVal(newField, remVal)
                newField = addFieldVal(newField, addVal)
            newLine = addDelimitedItem(newLine, newField, ';')
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
                newLine = self.setLineStatus(self.lineDict[romname], status)
                if child.checkState(0) == QtCore.Qt.Checked:
                    newLine = self.setFieldVal(newLine, 'Extra', '', 'excluded')
                else:
                    newLine = self.setFieldVal(newLine, 'Extra', 'excluded', '')
                self.lineDict[romname] = newLine

    def saveMame(self):
        try:
            if len(self.lineDict) > 0:
                self.updateLineDict()
                fileToOpen = os.path.join(self.configData.amDir, "romlists\\Mame.txt")
                with open(fileToOpen, "w") as of:
                    of.write(self.fileHeader)
                    for line in sorted(self.lineDict.values(), key=lambda kv: kv.split(';')[self.headerDict['Title']]):
                        of.write(line+'\n')
                self.dataChanged = False
                self.saveAct.setEnabled(False)
            
        except Exception as e:
            traceback.print_exc()
            raise e

    def addParent(self, treeItem, newTitle, romname, emu, category):
        gameIdx = self.treeWidget.topLevelItemCount()
        self.gameDict[romname] = gameIdx
        if newTitle not in self.titleDict:
            self.titleDict[newTitle] = gameIdx
        self.treeWidget.addTopLevelItem(QTreeWidgetItem(gameIdx))
        treeItem = self.treeWidget.topLevelItem(gameIdx)
        treeItem.setFlags(int(treeItem.flags()) | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsTristate)
        treeItem.setText(0, newTitle)
        treeItem.setText(5, emu)
        treeItem.setText(7, category)
        return treeItem

    def addChild(self, treeItem, newTitle, variation, romname, cloneOf, status, extra, category):
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
            childItem.setIcon(0, self.lockIcon)

        childItem.setText(0, newTitle)
        childItem.setText(1, variation)
        childItem.setText(2, romname)
        childItem.setText(3, cloneOf)
        childItem.setText(4, status)
        if romname in self.favList:
            childItem.setText(6, 'Yes')
        else:
            childItem.setText(6, '')
        childItem.setText(7, category)

        treeItem.insertChild(treeItem.childCount(), childItem)

    def loadTree(self, mode):
        if len(self.lineDict) == 0:
            return

        self.treeWidget.clear()
        app.processEvents()
        
        self.treeWidget.setSortingEnabled(False)
        self.gameDict.clear()
        self.titleDict.clear()

#        romnameCol = self.headerDict['Name']
        titleCol = self.headerDict['Title']
        cloneofCol = self.headerDict['CloneOf']
        statusCol = self.headerDict['Status']
        extraCol = self.headerDict['Extra']
        emuCol = self.headerDict['Emulator']
        catCol = self.headerDict['Category']

        d = QtWidgets.QDialog()
        dui = ProgressDialog(parent=self, flags=Qt.Dialog)
        dui.setupUi(d)
        d.show()
        dui.setProgressRange(1, len(self.lineDict)*2)

        idx = 0
        self.treeLoading = True
        
        for level in ('parent', 'child'):
            for romname, line in self.lineDict.items():
                try:
                    if dui.isCancelled():
                        break
                    wordlist = line.strip('\n\r').split(';')
                    cloneOf = wordlist[cloneofCol]
                    title = wordlist[titleCol]
                    status = getStatus(wordlist[statusCol])
                    extra = wordlist[extraCol]
                    newTitle, variation = getTitleVariation(title)
                    emu = wordlist[emuCol]
                    category = wordlist[catCol]

                    if mode == 'parent':
                        if level == 'parent':
                            if cloneOf == "":
                                treeItem = self.addParent(self.treeWidget, newTitle, romname, emu, category)
                                self.addChild(treeItem, newTitle, variation, romname, cloneOf, status, extra, category)
                        else:
                            if cloneOf != "":
                                if cloneOf in self.gameDict.keys():
                                    gameIdx = self.gameDict[cloneOf]
                                    treeItem = self.treeWidget.topLevelItem(gameIdx)
                                else:
                                    # Parent ROM not found, create dummy parent using cloneOf value
                                    treeItem = self.addParent(self.treeWidget, cloneOf, cloneOf, emu, category)
                                self.addChild(treeItem, newTitle, variation, romname, cloneOf, status, extra, category)
                    elif mode == 'title':
                        if level == 'parent':
                            if newTitle not in self.titleDict:
                                self.addParent(self.treeWidget, newTitle, romname, emu, category)
                        else:
                            gameIdx = self.titleDict[newTitle]
                            treeItem = self.treeWidget.topLevelItem(gameIdx)
                            self.addChild(treeItem, newTitle, variation, romname, cloneOf, status, extra, category)
                    idx += 1
                    dui.setProgressValue(idx)
                    if idx % 100 == 0:
                        app.processEvents()
                except Exception as e:
                    traceback.print_exc()
                    raise e
        self.treeLoading = False
        self.treeWidget.setSortingEnabled(True)
        self.statusBar().showMessage(
            str(self.treeWidget.topLevelItemCount()) + " Groups containing " + str(len(self.lineDict)) + " games")
        
    def loadList(self, listName):
        try:
            bkpFile = ''
            fileToOpen = os.path.join(self.configData.amDir, "romlists\\" + listName + ".txt")
            if os.path.exists(fileToOpen):
                self.dataChanged = False
                self.treeWidget.clear()
                self.lineDict.clear()
                self.gameDict.clear()
                self.headerDict.clear()

                self.treeWidget.setSortingEnabled(False)
                with open(fileToOpen) as fp:
                    line = fp.readline()
                    if line:
                        self.fileHeader = line
                        headerlist = line.strip('# \n').split(';')
                        for i, header in enumerate(headerlist):
                            self.headerDict[header] = i
                    else:
                        print("No header for ", listName)
                        return

                    self.emuDict.clear()
                    line = fp.readline()
                    while line:
                        wordlist = line.strip('\n\r').split(';')
                        romname = wordlist[self.headerDict['Name']]
                        emuname = wordlist[self.headerDict['Emulator']]
                        self.lineDict[romname] = line.strip('\n')
                        if emuname not in self.emuDict.keys():
                            self.emuDict[emuname] = 'None'
                        line = fp.readline()
                    self.addMenu('Emulator', self.emuDict, self.loadDisp)

                if self.firstLoad:
                    bkpFile = os.path.join(fileToOpen+".bkp")
                    with open(bkpFile, "w") as of:
                        of.write(self.fileHeader)
                        for line in self.lineDict.values():
                            of.write(line+'\n')
                    self.firstLoad = False

                fileToOpen = os.path.join(self.configData.amDir, "romlists\\" + listName + ".tag")
                if os.path.exists(fileToOpen):
                    with open(fileToOpen) as fp:
                        line = fp.readline()
                        while line:
                            fav_rom = line.strip('\n\r')
                            self.favList.append(fav_rom)
                            line = fp.readline()

                self.loadTree('parent')

                app.processEvents()

                self.treeWidget.setSortingEnabled(True)
                self.treeWidget.sortByColumn(0, Qt.AscendingOrder)
                self.treeWidget.sortByColumn(3, Qt.AscendingOrder)
                self.treeWidget.resizeColumnToContents(0)
                self.treeWidget.collapseAll()
                self.expColBtn.setText("Expand")

        except Exception as e:
            traceback.print_exc()
            raise e

    def getMameVersion(self):
        ret = subprocess.run(
            ["e:\\mame\\mame64.exe", "-version"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        print(ret)

    def processRom(self, romname):
        ret = subprocess.run(
            [self.configData.mameExe, romname, "-verifyroms", "-rompath", self.romPath],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)

#        if ret.stdout != "":
#            linelist = list(enumerate(ret.stdout.split('\n')))
#        else:
#            linelist = list(enumerate(ret.stderr.split('\n')))
#
#        for i, l in reversed(linelist):
#            wl = l.split(' ')
#            if wl[0] == "romset":
#                break
            
#        return ret.returncode, l
        return ret.returncode

#    def msgbtn(self, i):
#        print("Button pressed is {}".format(i.text()))

    def processList(self):
        pIdx = 0
        try:
            if not os.path.isfile(self.configData.mameExe):
                showErr('Invalid Mame executable, please fix and retry')
                return
            if os.path.isdir(self.configData.amDir):
                fileToOpen = os.path.join(self.configData.amDir, "emulators\\Mame.cfg")
                if not os.path.isfile(fileToOpen):
                    showErr('Unable to find {}, please fix and retry'.format(fileToOpen))
                    return
                self.romPath = getRomPath(fileToOpen)
            else:
                showErr('Invalid Attractmode directory, please fix and retry')
                return
            
            root = self.treeWidget.invisibleRootItem()
            titleCount = root.childCount()
            if titleCount == 0:
                showErr('No entries in list.  Please load Mame.txt before validating!')
                return
            d = QtWidgets.QDialog()
            self.treeWidget.expandAll()
            self.expColBtn.setText("Collapse")
            dui = ProgressDialog(parent=self, flags=Qt.Dialog)
            dui.setupUi(d)
            d.show()
            romCount = 0
            for idx in range(titleCount):
                romCount += root.child(idx).childCount()
            dui.setProgressRange(1, romCount)
            self.dataChanged = True
            for idx in range(titleCount):
                if dui.isCancelled():
                    break
                item = root.child(idx)
                for cIdx in range(item.childCount()):
                    pIdx += 1
                    child = item.child(cIdx)
                    romname = child.text(2)
#                    return_code, statusMsg = self.processRom(romname)
                    return_code = self.processRom(romname)
                    if return_code != 0:
                        child.setCheckState(0, Qt.Unchecked)
                        child.setText(4, 'fail')
                    else:
                        child.setText(4, 'pass')                        
                dui.setProgressValue(pIdx)
                self.statusBar().showMessage("{0} / {1}".format(pIdx, romCount))
                app.processEvents()
        except Exception as e:
            traceback.print_exc()
            raise e

    def findDuplicates(self):
        try:
            self.setTreeHidden(True)
            root = self.treeWidget.invisibleRootItem()
            titleCount = root.childCount()

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
                            checkedCount += 1
                            if checkedCount == 1:
                                variation = child.text(1)
                                romname = child.text(2)
                            
                    if checkedCount > 1:
                        item.setHidden(False)
                    else:
                        item.setText(1, variation)
                        item.setText(2, romname)
                        item.setText(4, 'Good')
                        
                    for cIdx in range(item.childCount()):
                        child = item.child(cIdx)
                        if child.checkState(0) == QtCore.Qt.Checked:
                            child.setHidden(False)

#            regFont = QFont()
#            regFont.setBold(False)
#            boldFont = QFont()
#            boldFont.setBold(True)
#            root = self.treeWidget.invisibleRootItem()
#            titleCount = root.childCount()
#            self.treeWidget.setSortingEnabled(False)
#            for idx in range(titleCount):
#                item = root.child(idx)
#                if item.checkState(0) == QtCore.Qt.Unchecked:
#                    item.setText(4, 'Excluded')
#                else:
#                    romname = ""
#                    variation = ""
#                    checkedCount = 0
#                    for cIdx in range(item.childCount()):
#                        child = item.child(cIdx)
#                        if child.checkState(0) == QtCore.Qt.Checked:
#                            if romname != "":
#                                item.setFont(0, boldFont)
#                                romname = ""
#                                item.setText(4, 'Duplicates')
#                                break
#                            variation = child.text(1)
#                            romname = child.text(2)
#                    if romname != "":
#                        item.setFont(0, regFont)
#                        item.setText(1, variation)
#                        item.setText(2, romname)
#                        item.setText(4, 'Good')
#            self.treeWidget.setSortingEnabled(True)
        except Exception as e:
            traceback.print_exc()
            raise e

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
                            if (child.checkState(0) == QtCore.Qt.Checked
                                    and child.text(3) == parentRom and child.text(5) != 'Yes'):
                                child.setCheckState(0, Qt.Unchecked)
            self.findDuplicates()
        except Exception as e:
            traceback.print_exc()
            raise e

    def setFailedHidden(self, hidden):
        try:
            root = self.treeWidget.invisibleRootItem()
            titleCount = root.childCount()
            for idx in range(titleCount):
                item = root.child(idx)
                pass_cnt = 0
                fail_cnt = 0
                other_cnt = 0
                for cIdx in range(item.childCount()):
                    child = item.child(cIdx)
                    if child.text(4) == "fail":
                        child.setHidden(hidden)
                        fail_cnt += 1
                    elif child.text(4) == "pass":
                        pass_cnt += 1
                    else:
                        other_cnt += 1
                if hidden == True and pass_cnt == 0 and other_cnt == 0:
                    item.setHidden(True)
                else:
                    item.setHidden(False)

        except Exception as e:
            traceback.print_exc()
            raise e

    def toggleFailed(self):
        if self.failedBtn.text() == 'Hide Failed':
            self.setFailedHidden(True)
            self.failedBtn.setText('Show Failed')
        else:
            self.setFailedHidden(False)
            self.failedBtn.setText('Hide Failed')

    def applyFailed(self):
        if self.failedBtn.text() == 'Hide Failed':
            self.setFailedHidden(False)
        else:
            self.setFailedHidden(True)

    def clearSearch(self):
        self.setTreeHidden(False)
        self.applyFailed()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = Ui_MainWindow()
    MainWindow.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
