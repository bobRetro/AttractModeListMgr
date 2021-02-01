import traceback
import subprocess
import os.path
import functools

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import *
from PyQt5.QtWidgets import QTreeWidgetItem

from ProgressDialog import ProgressDialog
from ConfigDialog import Ui_configDialog
from AmConfig import AmConfig
from recordtype import recordtype
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


def showMsg(windowTitle, message):
    try:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        msg.setText(message)
#            msg.setInformativeText("This is additional information")
        msg.setWindowTitle(windowTitle)
        msg.setStandardButtons(QMessageBox.Ok)
#            msg.buttonClicked.connect(self.msgbtn)

        retval = msg.exec_()
        return retval
    except Exception as msgException:
        traceback.print_exc()
        raise msgException


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


def getTitleVariation(title):
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
    valList = field.split(',')
    if val in valList:
        newField = ""
        for j in valList:
            if j != val:
                newField = addDelimitedItem(newField, j, ",")
    else:
        newField = field
    return newField


def addFieldVal(field, val):
    if val == '':
        return field
    newField = field
    valList = field.split(',')
    if val not in valList:
        newField = addDelimitedItem(newField, val, ",")
    return newField


class Ui_MainWindow(QMainWindow):
    dataChanged = False
    fileHeader = str()
    romItem = recordtype('romItem',
                         [('lstLine',  ''),
                          ('treeIdx',  '-1'),
                          ('excluded', 'N'),
                          ('locked',   'N'),
                          ('favorite', 'N'),
                          ('status',   'unknown')])
    romDict = dict()
    lineHeaderDict = dict()
    parentCloneOfDict = dict()
    parentTitleDict = dict()
    dispDict = dict()
    emuDict = dict()
    resultItems = list()
    searchOn = False
    findText = ''
    findField = ''
    hideUncheckedOn = False

    favList = list()
    configData = AmConfig()
    configfile = 'AttractModeMameListMgr.cfg'
    groupMode = 'parent'
    mameCfg = recordtype('mameCfg', [('rompath', ''), ('workdir', '')])
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
        self.unlockIcon = QtGui.QIcon("unlock.ico")
        self.starIcon = QtGui.QIcon("star.ico")
        self.blankIcon = QtGui.QIcon()
        self.findDlg = QtWidgets.QDialog()
        self.findUi = Ui_findDlg(parent=self)
        self.findUi.setupUi(self.findDlg)

        self.configDialog = QtWidgets.QDialog()
        self.configUi = Ui_configDialog(parent=self)
        self.configUi.setupUi(self.configDialog)

    def setupUi(self):
        self._windowLayout()
        # Dictates the order of the columns
        self.column_headers = ['Name', 'Variation', 'Rom', 'CloneOf', 'Category', 'Status', 'Emulator', 'Favorite']
        for idx, header in enumerate(self.column_headers):
            self.treeWidget.headerItem().setText(idx, header)
        self.col_name           = self.column_headers.index('Name')
        self.col_variation      = self.column_headers.index('Variation')
        self.col_rom            = self.column_headers.index('Rom')
        self.col_cloneof        = self.column_headers.index('CloneOf')
        self.col_category       = self.column_headers.index('Category')
        self.col_status         = self.column_headers.index('Status')
        self.col_emulator       = self.column_headers.index('Emulator')
        self.col_favorite       = self.column_headers.index('Favorite')

        self.startBtn.clicked.connect(self.processList)
        self.cloneBtn.clicked.connect(self.unselectClones)
        self.expColBtn.clicked.connect(self.expColTree)
        self.parentBtn.setChecked(True)
        self.groupMode = 'parent'
        self.parentBtn.toggled.connect(self.toggleParentMode)
        self.titleBtn.toggled.connect(self.toggleParentMode)
        self.clearSearchBtn.clicked.connect(self.clearSearch)
        self.failedBtn.clicked.connect(self.toggleUncheckedHidden)

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
        fileMenu.aboutToShow.connect(self.updateFileMenu)

        self.treeWidget.setSortingEnabled(True)
        self.retranslateUi()

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.loadAmConfigFile()

    def loadMameCfg(self):
        try:
            fileToOpen = os.path.join(self.configData.amDir, "emulators\\Mame.cfg")
            if not os.path.isfile(fileToOpen):
                showMsg('Error', 'Unable to find {}, please fix and retry'.format(fileToOpen))
                return

            if os.path.isfile(fileToOpen):
                with open(fileToOpen, "r") as fp:
                    line = fp.readline()
                    while line:
                        lvl, key, val = getCfgLineKeyVal(line)
                        if key == 'rompath':
                            self.mameCfg.rompath = val
                        if key == 'workdir':
                            self.mameCfg.workdir = val
                        line = fp.readline()
        except Exception as e:
            traceback.print_exc()
            raise e

    def menuContextTree(self, point):
        index = self.treeWidget.indexAt(point)

        if not index.isValid():
            return

#            item = self.treeWidget.itemAt(point)
#            name = item.text(self.col_name)  # The text of the node.

        # Context menu
        menu = QtWidgets.QMenu()
        self.setLockedContextMenu(menu, point)
        menu.addSeparator()
        self.setCheckedContextMenu(menu, point)
        menu.addSeparator()
        self.setFavoriteContextMenu(menu, point)
        menu.addSeparator()
        self.setValidateContextMenu(menu, point)

        menu.exec_(self.treeWidget.mapToGlobal(point))

    def addMenu(self, menuName, subMenuDict, connectAction):
        dispMenu = None
        # Attempt to find menu by name
        for m in self.menuBar().children():
            if isinstance(m, QMenu) and m.title() == menuName:
                dispMenu = m
                break
        # If menu is not found create it
        if not isinstance(dispMenu, QMenu):
            dispMenu = self.menuBar().addMenu(menuName)

        # Clear out the menu
        for a in dispMenu.actions():
            dispMenu.removeAction(a)

        # Add the diplays as submenus
        for s in subMenuDict.keys():
            dispAct = QAction(s, self)
            dispAct.triggered.connect(connectAction)

            dispMenu.addAction(dispAct)

    def loadAmConfig(self, fileToOpen):
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
        else:
            showMsg('Error',
                    'Unable to find AttractMode config file.  Please go to preferences and select the AttractMode '
                    'directory and ensure a config file exists')
        return dispDict

    def loadAmConfigFile(self):
        if os.path.exists(self.configfile):
            self.configData.loadJSON(self.configfile)
            self.configUi.amDir.setText(self.configData.amDir)
            self.configUi.mameExe.setText(self.configData.mameExe)
            self.dispDict = self.loadAmConfig(os.path.join(self.configData.amDir, "attract.cfg"))
            self.addMenu('Display', self.dispDict, self.loadDisplay)
            if 'Mame' in self.dispDict:
                self.loadList('Mame')

    def showPreferences(self):
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

    def ignoreUnsavedChangesWarning(self):
        ignore = True
        if self.dataChanged:
            reply = QMessageBox.question(self,
                                         "Unsaved Changes",
                                         "There are unsaved changes. Are you sure you want to exit?",
                                         QMessageBox.Yes,
                                         QMessageBox.No)
            if reply != QMessageBox.Yes:
                ignore = False
        return ignore

    def loadDisplay(self):
        if self.ignoreUnsavedChangesWarning():
            self.dataChanged = False
            action = self.sender()
            self.loadList(action.text())

    def closeProgram(self):
        self.close()

    def closeEvent(self, event):
        if self.ignoreUnsavedChangesWarning():
            event.accept()
        else:
            event.ignore()

    def showFindDlg(self):
        self.findDlg.show()
        self.findUi.findLineClicked()
        self.findUi.findBtn.setAutoDefault(True)
        self.findUi.findLine.setFocus()
        
#    def keyPressEvent(self, e):
#        if e.key() == Qt.Key_Escape:
#            self.close()
    
    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate(   "MainWindow", "Attract Mode List Manager"))
        self.cloneBtn.setText(_translate(       "MainWindow", "Unselect Clones"))
        self.label.setText(_translate(          "MainWindow", "Group Mode"))
        self.parentBtn.setText(_translate(      "MainWindow", "Parent"))
        self.titleBtn.setText(_translate(       "MainWindow", "Title"))
        self.startBtn.setText(_translate(       "MainWindow", "Validate"))
        self.expColBtn.setText(_translate(      "MainWindow", "Expand"))
        self.failedBtn.setText(_translate(      "MainWindow", "Hide Unchecked"))
        self.clearSearchBtn.setText(_translate( "MainWindow", "Clear Search"))
        self.treeWidget.setSortingEnabled(True)

    def updateFileMenu(self):
        if self.dataChanged:
            self.saveAct.setEnabled(True)

    def treeItemChanged(self, item, column):
        if not self.treeLoading:
            self.dataChanged = True
            if item.parent():
                romName = item.text(self.col_rom)
                newLine = self.romDict[romName].lstLine

                if column == self.col_status:
                    status = item.text(self.col_status)
                    self.romDict[romName].status = status

                if column == self.col_name:
                    if item.checkState(0) == QtCore.Qt.Checked:
                        newLine = self.removeLineFieldVal(newLine, 'Extra', 'excluded')
                        self.romDict[romName].excluded = 'N'
                    else:
                        newLine = self.addLineFieldVal(newLine, 'Extra', 'excluded')
                        self.romDict[romName].excluded = 'Y'

                self.romDict[romName].lstLine = newLine

    def toggleParentMode(self):
        radioButton = self.sender()
        if radioButton.isChecked():
            if radioButton.objectName() == 'parentBtn':
                self.groupMode = 'parent'
            elif radioButton.objectName() == 'titleBtn':
                self.groupMode = 'title'
            self.loadTree(self.groupMode)
            self.treeWidget.expandAll()
            self.expColBtn.setText("Collapse")
        if self.hideUncheckedOn:
            self.setUncheckedHidden(True)
        if self.searchOn and self.findField != "" and self.findText != "":
            self.searchList(self.findField, self.findText)

    def searchLineClicked(self):
        self.searchBtn.setDefault(True)
        self.searchBtn.setAutoDefault(True)

    def getLineField(self, line, field):
        if field in self.lineHeaderDict.keys():
            return line.split(';')[self.lineHeaderDict[field]]
        else:
            return None

    def getSelectedExtraFieldCount(self, extra_field):
        item_count = 0
        field_count = 0
        selected_items = self.treeWidget.selectedItems()
        for tree_item in selected_items:
            if tree_item.parent():
                item_count += 1
                newLine = self.romDict[tree_item.text(self.col_rom)].lstLine
                extra = self.getLineField(newLine, 'Extra')
                if extra_field in extra.split(','):
                    field_count += 1
        return item_count, field_count

    def getSelectedColValueCount(self, column_name, col_value):
        item_count = 0
        value_count = 0
        selected_items = self.treeWidget.selectedItems()
        for tree_item in selected_items:
            rom_name = tree_item.text(self.col_rom)
            if tree_item.parent():
                item_count += 1
                if (column_name == 'locked'   and self.romDict[rom_name].locked   == col_value or
                        column_name == 'favorite' and self.romDict[rom_name].favorite == col_value or
                        column_name == 'status'   and self.romDict[rom_name].status   == col_value):
                    value_count += 1
        return item_count, value_count

    def lockItem(self, tree_item):
        if tree_item.parent():
            tree_item.setIcon(0, self.lockIcon)
            self.romDict[tree_item.text(self.col_rom)].locked = 'Y'

    def unlockItem(self, tree_item):
        if tree_item.parent():
            tree_item.setIcon(0, self.unlockIcon)
            self.romDict[tree_item.text(self.col_rom)].locked = 'N'

    def setSelectedLockStatus(self, status):
        selected_items = self.treeWidget.selectedItems()
        for tree_item in selected_items:
            if tree_item.parent():
                if status == 'lock':
                    self.lockItem(tree_item)
                elif status == 'unlock':
                    self.unlockItem(tree_item)
                elif status == 'toggle':
                    if self.romDict[tree_item.text(self.col_rom)].locked == 'Y':
                        self.unlockItem(tree_item)
                    else:
                        self.lockItem(tree_item)

    def setLockedContextMenu(self, menu, point):
        name = ""
        item_count, locked_count = self.getSelectedColValueCount('locked', 'N')

        if item_count > 0:
            if item_count == 1:
                name = " "+self.treeWidget.itemAt(point).text(self.col_name)

            if locked_count > 0 and locked_count != item_count:
                action = menu.addAction("Toggle locked")
                action.triggered.connect(functools.partial(self.setSelectedLockStatus, 'toggle'))

            if locked_count > 0:
                action = menu.addAction("Lock"+name)
                action.triggered.connect(functools.partial(self.setSelectedLockStatus, 'lock'))

            if locked_count < item_count:
                action = menu.addAction("Unlock"+name)
                action.triggered.connect(functools.partial(self.setSelectedLockStatus, 'unlock'))

    def favoriteItem(self, tree_item):
        if tree_item.parent() and self.romDict[tree_item.text(self.col_rom)].locked == 'N':
            tree_item.setIcon(self.col_favorite, self.starIcon)
            self.romDict[tree_item.text(self.col_rom)].favorite = 'Y'

    def unfavoriteItem(self, tree_item):
        if tree_item.parent() and self.romDict[tree_item.text(self.col_rom)].locked == 'N':
            tree_item.setIcon(self.col_favorite, self.blankIcon)
            self.romDict[tree_item.text(self.col_rom)].favorite = 'N'

    def setSelectedFavoriteStatus(self, status):
        selected_items = self.treeWidget.selectedItems()
        for tree_item in selected_items:
            if tree_item.parent():
                if status == 'favorite':
                    self.favoriteItem(tree_item)
                elif status == 'unfavorite':
                    self.unfavoriteItem(tree_item)
                elif status == 'toggle':
                    if self.romDict[tree_item.text(self.col_rom)].favorite == 'Y':
                        self.unfavoriteItem(tree_item)
                    else:
                        self.favoriteItem(tree_item)

    def setFavoriteContextMenu(self, menu, point):
        name = ""
        item_count, favorite_count = self.getSelectedColValueCount('favorite', 'N')

        if item_count > 0:
            if item_count == 1:
                name = " "+self.treeWidget.itemAt(point).text(self.col_name)

            if favorite_count > 0 and favorite_count != item_count:
                action = menu.addAction("Toggle favorites")
                action.triggered.connect(functools.partial(self.setSelectedFavoriteStatus, 'toggle'))

            if favorite_count > 0:
                action = menu.addAction("Add"+name+" to favorites")
                action.triggered.connect(functools.partial(self.setSelectedFavoriteStatus, 'favorite'))

            if favorite_count < item_count:
                action = menu.addAction("Unlock"+name+" to favorites")
                action.triggered.connect(functools.partial(self.setSelectedLockStatus, 'unfavorite'))

    def validateSelected(self, status):
        if os.path.isdir(self.configData.amDir):
            self.loadMameCfg()
        else:
            showMsg('Error', 'Invalid Attractmode directory, please fix and retry')
            return

        pass_count = 0
        fail_count = 0
        rom_name   = ''

        selected_items = self.treeWidget.selectedItems()

        d = QtWidgets.QDialog()
        dui = ProgressDialog(parent=self, flags=Qt.Dialog)
        dui.setupUi(d)
        d.show()
        dui.setProgressRange(1, len(selected_items))

        s = ''
        for idx, tree_item in enumerate(selected_items):
            if tree_item.parent():
                if (status == 'all'
                    or status == 'passed' and tree_item.text(self.col_status) == 'pass'
                        or status == 'failed' and tree_item.text(self.col_status) == 'fail'):
                    rom_name = tree_item.text(self.col_rom)
                    s = self.validateTreeItem(tree_item)
                    if s == 'pass':
                        pass_count += 1
                    else:
                        fail_count += 1
                    app.processEvents()
                    dui.setProgressValue(idx+1)

        dui.setProgressValue(len(selected_items))
        app.processEvents()
        if pass_count + fail_count == 0:
            message = 'No Games selected to validate'
        elif pass_count + fail_count == 1:
            message = '{} {}ed'.format(rom_name, s)
        else:
            message = 'Validated {} roms: {} passed and {} failed'.format(pass_count + fail_count, pass_count,
                                                                          fail_count)
        showMsg('Validation Results', message)

    def setValidateContextMenu(self, menu, point):
        name = ""
        item_count, fail_count = self.getSelectedColValueCount('status', 'fail')

        if item_count > 0:
            if item_count == 1:
                name = " "+self.treeWidget.itemAt(point).text(self.col_name)

            if fail_count == 0 or fail_count == item_count:
                action = menu.addAction("Validate"+name)
                action.triggered.connect(functools.partial(self.validateSelected, 'all'))
            else:
                action = menu.addAction("Validate failed")
                action.triggered.connect(functools.partial(self.validateSelected, 'failed'))
                action = menu.addAction("Validate passed")
                action.triggered.connect(functools.partial(self.validateSelected, 'passed'))
                action = menu.addAction("Validate all")
                action.triggered.connect(functools.partial(self.validateSelected, 'all'))

    def setSelectedCheckStatus(self, status):
        selected_items = self.treeWidget.selectedItems()
        for tree_item in selected_items:
            if tree_item.parent() and self.romDict[tree_item.text(self.col_rom)].locked == 'N':
                if status == 'check':
                    tree_item.setCheckState(0, Qt.Checked)
                elif status == 'uncheck':
                    tree_item.setCheckState(0, Qt.Unchecked)
                elif status == 'toggle':
                    if tree_item.checkState(self.col_name) == QtCore.Qt.Checked:
                        tree_item.setCheckState(0, Qt.Unchecked)
                    else:
                        tree_item.setCheckState(0, Qt.Checked)

    def setCheckedContextMenu(self, menu, point):
        name = ""
        item_count, unchecked_count = self.getSelectedExtraFieldCount('excluded')

        if item_count > 0:
            if item_count == 1:
                name = " "+self.treeWidget.itemAt(point).text(self.col_name)

            if unchecked_count > 0 and unchecked_count != item_count:
                action = menu.addAction("Toggle checked")
                action.triggered.connect(functools.partial(self.setSelectedCheckStatus, 'toggle'))

            if unchecked_count > 0:
                action = menu.addAction("Check"+name)
                action.triggered.connect(functools.partial(self.setSelectedCheckStatus, 'check'))

            if unchecked_count < item_count:
                action = menu.addAction("Uncheck"+name)
                action.triggered.connect(functools.partial(self.setSelectedCheckStatus, 'uncheck'))

    def setTreeHidden(self, hidden):
        root = self.treeWidget.invisibleRootItem()
        titleCount = root.childCount()
        for idx in range(titleCount):
            item = root.child(idx)
            item.setHidden(hidden)
            for cIdx in range(item.childCount()):
                child = item.child(cIdx)
                child.setHidden(hidden)

    def showSearchResults(self):
        for item in self.resultItems:
            if not self.hideUncheckedOn or item.checkState(0) == Qt.Checked:
                item.setHidden(False)
                if item.parent():
                    item.parent().setHidden(False)
                    if self.findUi.cbxInclSiblings.isChecked():
                        for cIdx in range(item.parent().childCount()):
                            if not self.hideUncheckedOn or item.parent().child(cIdx).checkState(0) == Qt.Checked:
                                item.parent().child(cIdx).setHidden(False)

        # for item in self.resultItems:
        #     if not item.parent() and not item.isHidden():
        #         showParent = False
        #         for cIdx in range(item.childCount()):
        #             if not item.child(cIdx).isHidden():
        #                 showParent = True
        #         if showParent:
        #             item.setHidden(True)

    def searchList(self, field, searchTerm):
        if searchTerm != "" and field != "":
            self.findField = field
            self.findText = searchTerm

            self.setTreeHidden(True)

            if self.findUi.cbxExactMatch.isChecked():
                searchFlags = QtCore.Qt.MatchExactly
            else:
                searchFlags = QtCore.Qt.MatchContains

            if self.findUi.cbxChildren.isChecked():
                searchFlags |= QtCore.Qt.MatchRecursive

            self.resultItems = self.treeWidget.findItems(searchTerm, searchFlags, self.column_headers.index(field))
            self.showSearchResults()
            self.searchOn = True
            self.showStatus()

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
            
    def openAmDirDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName = str(QFileDialog.getExistingDirectory())
        if fileName:
            self.amDir.setText(os.path.normpath(fileName))

    def openMameExeDialog(self):
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

    def addRemoveLineFieldVal(self, line, field, addVal, remVal):
        newLine = ""
        colList = line.split(';')
        for i, h in enumerate(self.lineHeaderDict):
            newField = colList[i]
            if h == field:
                newField = removeFieldVal(newField, remVal)
                newField = addFieldVal(newField, addVal)
            newLine = addDelimitedItem(newLine, newField, ';')
        return newLine

    def addLineFieldVal(self, line, field, fieldVal):
        return self.addRemoveLineFieldVal(line, field, fieldVal, '')

    def removeLineFieldVal(self, line, field, fieldVal):
        return self.addRemoveLineFieldVal(line, field, '', fieldVal)

    def saveAlm(self):
        fileToOpen = os.path.join(self.configData.amDir, "romLists\\Mame.alm")
        with open(fileToOpen, "w") as of:
            of.write('#Name,Excluded,Locked,Status\n')
            for romItem in sorted(self.romDict.values(),
                                  key=lambda kv: kv.lstLine.split(';')[self.lineHeaderDict['Title']]):
                wordList = romItem.lstLine.strip('\n\r').split(';')
                rom = wordList[self.lineHeaderDict['Name']]
                if self.romDict[rom].locked == 'Y' or self.romDict[rom].excluded == 'Y' or\
                        self.romDict[rom].status != '':
                    newLine = rom
                    if self.romDict[rom].excluded == 'Y':
                        newLine += ',Y'
                    else:
                        newLine += ',N'
                    if self.romDict[rom].locked == 'Y':
                        newLine += ',Y'
                    else:
                        newLine += ',N'
                    if self.romDict[rom].status != '':
                        newLine += ','+self.romDict[rom].status
                    else:
                        newLine += ',unknown'
                    of.write(newLine+'\n')

    def saveMame(self):
        if len(self.romDict) > 0:
            fileToOpen = os.path.join(self.configData.amDir, "romlists\\Mame.txt")
            with open(fileToOpen, "w") as of:
                of.write(self.fileHeader)
                for romItem in sorted(self.romDict.values(), key=lambda kv: kv.lstLine.split(';')[self.lineHeaderDict['Title']]):
                    line = self.removeLineFieldVal(romItem.lstLine, 'Status', 'pass')
                    of.write(line+'\n')
            self.saveAlm()
            self.dataChanged = False
            self.saveAct.setEnabled(False)

    def addParent(self, newTitle, romname, emu, category):
        gameIdx = self.treeWidget.topLevelItemCount()
        self.parentCloneOfDict[romname] = gameIdx
        # if romname in self.romDict:
        #     self.romDict[romname].treeIdx = gameIdx
        # else:
        #     self.romDict[romname] = self.romItem(treeIdx=gameIdx)
        if newTitle not in self.parentTitleDict:
            self.parentTitleDict[newTitle] = gameIdx
        self.treeWidget.addTopLevelItem(QTreeWidgetItem(gameIdx))
        treeItem = self.treeWidget.topLevelItem(gameIdx)
        treeItem.setFlags(int(treeItem.flags()) | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsTristate)
        treeItem.setText(self.col_name, newTitle)
        treeItem.setText(self.col_emulator, emu)
        treeItem.setText(self.col_category, category)
        return treeItem

    def addChild(self, treeItem, newTitle, variation, romname, cloneOf, status, extra, category):

        childItem = QTreeWidgetItem()
        extraList = extra.split(',')

        if romname in self.romDict and self.romDict[romname].excluded == 'Y':
            childItem.setCheckState(0, Qt.Unchecked)
        else:
            childItem.setCheckState(0, Qt.Checked)

        childItem.setText(self.col_name,        newTitle)
        childItem.setText(self.col_variation,   variation)
        childItem.setText(self.col_rom,         romname)
        childItem.setText(self.col_cloneof,     cloneOf)
        childItem.setText(self.col_status,      status)

        if romname in self.favList:
            childItem.setIcon(self.col_favorite, self.starIcon)
            self.romDict[childItem.text(self.col_rom)].favorite = 'Y'
        else:
            childItem.setIcon(self.col_favorite, self.blankIcon)
            self.romDict[childItem.text(self.col_rom)].favorite = 'N'

        childItem.setText(self.col_category, category)

        treeItem.insertChild(treeItem.childCount(), childItem)
        childItem = treeItem.child(treeItem.childCount()-1)

        # Has to be after child is added because only child items can be locked
        if romname in self.romDict and self.romDict[romname].locked == 'Y':
            self.lockItem(childItem)
        else:
            self.unlockItem(childItem)

    def showStatus(self):
        root = self.treeWidget.invisibleRootItem()
        titleCount = root.childCount()
        hiddenGroupCount = 0
        hiddenChildCount = 0
        #self.treeWidget.topLevelItemCount()
        for idx in range(titleCount):
            item = root.child(idx)
            if item.isHidden():
                hiddenGroupCount += 1
            for cIdx in range(item.childCount()):
                child = item.child(cIdx)
                if child.isHidden():
                    hiddenChildCount += 1

        if hiddenGroupCount > 0 or hiddenChildCount >0:
            self.statusBar().showMessage(
                "{} Groups ({} hidden) containing {} games ({} hidden)".format(titleCount, hiddenGroupCount, len(self.romDict), hiddenChildCount))
        else:
            self.statusBar().showMessage(
                "{} Groups containing {} games".format(titleCount, len(self.romDict)))

    def loadTree(self, mode):
        if len(self.romDict) == 0:
            return

        self.treeWidget.clear()
        app.processEvents()
        
        self.treeWidget.setSortingEnabled(False)
        self.parentCloneOfDict.clear()
        self.parentTitleDict.clear()

        titleCol = self.lineHeaderDict['Title']
        cloneofCol = self.lineHeaderDict['CloneOf']
        statusCol = self.lineHeaderDict['Status']
        extraCol = self.lineHeaderDict['Extra']
        emuCol = self.lineHeaderDict['Emulator']
        catCol = self.lineHeaderDict['Category']

        d = QtWidgets.QDialog()
        dui = ProgressDialog(parent=self, flags=Qt.Dialog)
        dui.setupUi(d)
        d.show()
        dui.setProgressRange(1, len(self.romDict)*2)

        idx = 0
        self.treeLoading = True
        
        for level in ('parent', 'child'):
            for romname, romItem in self.romDict.items():
                line = romItem.lstLine
                try:
                    if dui.isCancelled():
                        break
                    wordlist = line.strip('\n\r').split(';')
                    cloneOf = wordlist[cloneofCol]
                    title = wordlist[titleCol]
#                    status = getStatus(wordlist[statusCol])
#                    self.romDict[romname].status = status
                    status = self.romDict[romname].status
                    extra = wordlist[extraCol]
                    newTitle, variation = getTitleVariation(title)
                    emu = wordlist[emuCol]
                    category = wordlist[catCol]

                    if mode == 'parent':
                        if level == 'parent':
                            if cloneOf == "":
                                treeItem = self.addParent(newTitle, romname, emu, category)
                                self.addChild(treeItem, newTitle, variation, romname, cloneOf, status, extra, category)
                        else:
                            try:
                                if cloneOf != "":
                                    if cloneOf in self.parentCloneOfDict.keys():
                                        gameIdx = self.parentCloneOfDict[cloneOf]
                                        treeItem = self.treeWidget.topLevelItem(gameIdx)
                                    else:
                                        # Parent ROM not found, create dummy parent using cloneOf value
                                        treeItem = self.addParent(cloneOf, cloneOf, emu, category)
                                    self.addChild(treeItem, newTitle, variation, romname, cloneOf, status, extra,
                                                  category)
                                # if cloneOf != "":
                                #     if cloneOf in self.romDict.keys():
                                #         gameIdx = self.romDict[cloneOf].treeIdx
                                #         treeItem = self.treeWidget.topLevelItem(gameIdx)
                                #     else:
                                #         # Parent ROM not found, create dummy parent using cloneOf value
                                #         treeItem = self.addParent(cloneOf, cloneOf, emu, category)
                                #     self.addChild(treeItem, newTitle, variation, romname, cloneOf, status, extra, category)
                            except Exception as e:
                                print("failed "+romname)
                                #traceback.print_exc()
                                #raise e

                    elif mode == 'title':
                        if level == 'parent':
                            if newTitle not in self.parentTitleDict:
                                self.addParent(newTitle, romname, emu, category)
                        else:
                            gameIdx = self.parentTitleDict[newTitle]
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
        self.showStatus()

    def loadList(self, listName):
        try:
            bkpFile = ''

            fileToOpen = os.path.join(self.configData.amDir, "romlists\\" + listName + ".txt")
            if os.path.exists(fileToOpen):
                self.dataChanged = False
                self.treeWidget.clear()
                self.romDict.clear()
                self.parentCloneOfDict.clear()
                self.lineHeaderDict.clear()

                self.treeWidget.setSortingEnabled(False)
                with open(fileToOpen) as fp:
                    line = fp.readline()
                    if line:
                        self.fileHeader = line
                        headerlist = line.strip('# \n').split(';')
                        for i, header in enumerate(headerlist):
                            self.lineHeaderDict[header] = i
                    else:
                        print("No header for ", listName)
                        return

                    self.emuDict.clear()
                    line = fp.readline()
                    while line:
                        wordlist = line.strip('\n\r').split(';')
                        romname = wordlist[self.lineHeaderDict['Name']]
                        emuname = wordlist[self.lineHeaderDict['Emulator']]
                        self.romDict[romname] = self.romItem(lstLine=line.strip('\n'))
                        if emuname not in self.emuDict.keys():
                            self.emuDict[emuname] = 'None'
                        line = fp.readline()
                    self.addMenu('Emulator', self.emuDict, self.loadDisplay)

                if self.firstLoad:
                    bkpFile = os.path.join(fileToOpen+".bkp")
                    with open(bkpFile, "w") as of:
                        of.write(self.fileHeader)
                        for romItem in self.romDict.values():
                            of.write(romItem.lstLine+'\n')
                    self.firstLoad = False

                fileToOpen = os.path.join(self.configData.amDir, "romlists\\" + listName + ".tag")
                if os.path.exists(fileToOpen):
                    with open(fileToOpen) as fp:
                        line = fp.readline()
                        while line:
                            fav_rom = line.strip('\n\r')
                            self.favList.append(fav_rom)
                            line = fp.readline()

                fileToOpen = os.path.join(self.configData.amDir, "romlists\\" + listName + ".alm")

                if os.path.exists(fileToOpen):
                    with open(fileToOpen) as fp:
                        # Read in the header
                        #TODO actually use header
                        line = fp.readline().strip('\n')
                        line = fp.readline().strip('\n')
                        while line:
                            almFields = line.split(',')
                            if almFields[0] in self.romDict:
                                self.romDict[almFields[0]].excluded = almFields[1]
                                self.romDict[almFields[0]].locked = almFields[2]
                                self.romDict[almFields[0]].status = almFields[3]
                            else:
                                self.romDict[almFields[0]] = self.romItem(excluded=almFields[1], locked=almFields[2], status=almFields[3])
                            line = fp.readline().strip('\n')

                self.loadTree('parent')

                app.processEvents()

                self.treeWidget.setSortingEnabled(True)
                self.treeWidget.sortByColumn(self.col_name, Qt.AscendingOrder)
                self.treeWidget.sortByColumn(self.col_cloneof, Qt.AscendingOrder)
                self.treeWidget.resizeColumnToContents(self.col_name)
                self.treeWidget.expandAll()
                self.expColBtn.setText("Collapse")

        except Exception as e:
            traceback.print_exc()
            raise e

    def getMameVersion(self):
        ret = subprocess.run(
            ["e:\\mame\\mame64.exe", "-version"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        print('Found Mame version {}'.format(ret))

    def processRom(self, romname):
        ret = subprocess.run(
            [self.configData.mameExe, romname, "-verifyroms", "-rompath", self.mameCfg.rompath],
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

    def validateTreeItem(self, treeItem):
        try:
            rom_name = treeItem.text(self.col_rom)
            return_code = self.processRom(rom_name)
            if return_code != 0:
                treeItem.setCheckState(0, Qt.Unchecked)
                status = 'fail'
            else:
                status = 'pass'
            treeItem.setText(self.col_status, status)
            self.romDict[rom_name].status = status
            return status

        except Exception as e:
            traceback.print_exc()
            raise e
#    def msgbtn(self, i):
#        print("Button pressed is {}".format(i.text()))

    def processList(self):
        pIdx = 0
        try:
            if not os.path.isfile(self.configData.mameExe):
                showMsg('Error', 'Invalid Mame executable, please fix and retry')
                return

            if os.path.isdir(self.configData.amDir):
                self.loadMameCfg()
            else:
                showMsg('Error', 'Invalid Attractmode directory, please fix and retry')
                return

            root = self.treeWidget.invisibleRootItem()
            titleCount = root.childCount()
            if titleCount == 0:
                showMsg('Error', 'No entries in list.  Please load Mame.txt before validating!')
                return
            self.treeWidget.expandAll()
            self.expColBtn.setText("Collapse")
            d = QtWidgets.QDialog()
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
                    status = self.validateTreeItem(child)
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
                if item.checkState(0) == QtCore.Qt.Checked or item.checkState(0) == QtCore.Qt.PartiallyChecked:
                    romname = ""
                    variation = ""
                    checkedCount = 0
                    for cIdx in range(item.childCount()):
                        child = item.child(cIdx)
                        if child.checkState(0) == QtCore.Qt.Checked:
                            checkedCount += 1
                            if checkedCount == 1:
                                variation = child.text(self.col_variation)
                                romname = child.text(self.col_rom)
                            
                    if checkedCount > 1:
                        item.setHidden(False)
                    else:
                        item.setText(self.col_variation, variation)
                        item.setText(self.col_rom, romname)
                        item.setText(self.col_status, 'pass')
                        
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
                            if child.text(self.col_cloneof) == "":
                                if parentRom == "":
                                    parentRom = child.text(self.col_rom)
                                elif parentRom != child.text(self.col_rom):
                                    parentRom = ""
                                    break
                    if parentRom != "":
                        for cIdx in range(item.childCount()):
                            child = item.child(cIdx)
                            if (child.checkState(0) == QtCore.Qt.Checked
                                    and child.text(self.col_cloneof) == parentRom and self.romDict[child.text(self.col_rom)].locked == 'N'):
                                child.setCheckState(0, Qt.Unchecked)
#            self.findDuplicates()
        except Exception as e:
            traceback.print_exc()
            raise e

    def setUncheckedHidden(self, hidden):
        try:
            self.hideUncheckedOn = hidden
            if self.searchOn and not hidden:
                self.showSearchResults()
            else:
                root = self.treeWidget.invisibleRootItem()
                titleCount = root.childCount()
                for idx in range(titleCount):
                    item = root.child(idx)
                    checked_cnt = 0
                    unchecked_cnt = 0
                    other_cnt = 0
                    for cIdx in range(item.childCount()):
                        child = item.child(cIdx)
                        if child.checkState(0) == QtCore.Qt.Unchecked:
                            if hidden:
                                child.setHidden(True)
                            else:
                                if not self.searchOn:
                                    child.setHidden(False)
                            unchecked_cnt += 1
                        elif item.checkState(0) != QtCore.Qt.Unchecked:
                            if not self.searchOn:
                                child.setHidden(False)
                            if not child.isHidden():
                                checked_cnt += 1
                        else:
                            other_cnt += 1
                    if hidden and checked_cnt == 0 and other_cnt == 0:
                        item.setHidden(True)
                    else:
                        if not self.searchOn:
                            item.setHidden(False)

        except Exception as e:
            traceback.print_exc()
            raise e

    def toggleUncheckedHidden(self):
        if self.failedBtn.text() == 'Hide Unchecked':
            self.setUncheckedHidden(True)
            self.failedBtn.setText('Show Unchecked')
        else:
            self.setUncheckedHidden(False)
            self.failedBtn.setText('Hide Unchecked')
        self.showStatus()

    def applyUncheckedHidden(self):
        if self.failedBtn.text() == 'Hide Unchecked':
            self.setUncheckedHidden(False)
        else:
            self.setUncheckedHidden(True)

    def clearSearch(self):
        self.setTreeHidden(False)
        self.applyUncheckedHidden()
        self.findField = ''
        self.findText = ''
        self.searchOn = False

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Breeze')
    MainWindow = Ui_MainWindow()
    MainWindow.setupUi()
    MainWindow.show()
    try:
        sys.exit(app.exec_())
    except Exception as e:
        traceback.print_exc()
        raise e