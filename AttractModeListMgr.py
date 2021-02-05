import traceback
import subprocess
import os.path
import functools

import win32api

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


def loadDisplayCfg(cfgList, displayCfg, listIdx):
    filterName = ''
    displayCfg.filterDict = dict()
    for i in range(listIdx+1, len(cfgList)):
        line = cfgList[i]
        lvl, cfgKey, cfgVal = getCfgLineKeyVal(line)
        if lvl == 1:
            if cfgKey == 'filter':
                filterName = cfgVal
                displayCfg.filterDict[filterName] = list()
            else:
                displayCfg.cfgDict[cfgKey] = cfgVal
        elif lvl == 2 and cfgKey == 'rule':
            displayCfg.filterDict[filterName].append(cfgVal)
        elif lvl == 0:
            return i

    return len(cfgList)


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

# class AlignDelegate(QtWidgets.QStyledItemDelegate):
#     def initStyleOption(self, option, index):
#         super(AlignDelegate, self).initStyleOption(option, index)
#         option.displayAlignment = QtCore.Qt.AlignCenter


def getMameVersion(mamePath):
    ret = subprocess.run(
        [mamePath, "-version"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    return str(ret.stdout)


class Ui_MainWindow(QMainWindow):
    fileHeader = str()
    romItem = recordtype('romItem',
                         [('title',    ''),
                          ('lstLine',  ''),
                          ('treeIdx',  '-1'),
                          ('excluded', 'N'),
                          ('locked',   'N'),
                          ('favorite', 'N'),
                          ('status',   'unknown')])
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
    currentDisplay = ''
    windowTitle = "AttractMode List Manager"

#    favList = list()
    configData = AmConfig()
    configfile = 'AttractModeListMgr.cfg'
    groupMode = 'parent'
    mameCfg = recordtype('mameCfg', [('rompath', ''), ('workdir', ''), ('executable', '')])

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
        self.gridLayout.addWidget(self.cloneBtn, 1, 5, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 10, 1, 1)
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
        self.gridLayout.addWidget(self.treeWidget, 4, 0, 1, 12)
        self.clearSearchBtn = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.clearSearchBtn.sizePolicy().hasHeightForWidth())
        self.clearSearchBtn.setSizePolicy(sizePolicy)
        self.clearSearchBtn.setObjectName("clearSearchBtn")
        self.gridLayout.addWidget(self.clearSearchBtn, 1, 11, 1, 1)
        self.expColBtn = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.expColBtn.sizePolicy().hasHeightForWidth())
        self.expColBtn.setSizePolicy(sizePolicy)
        self.expColBtn.setObjectName("expColBtn")
        self.gridLayout.addWidget(self.expColBtn, 1, 3, 1, 1)
        self.frame = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
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
        self.uncheckedBtn = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uncheckedBtn.sizePolicy().hasHeightForWidth())
        self.uncheckedBtn.setSizePolicy(sizePolicy)
        self.uncheckedBtn.setObjectName("uncheckedBtn")
        self.gridLayout.addWidget(self.uncheckedBtn, 1, 4, 1, 1)
        self.findDupButton = QtWidgets.QPushButton(self.centralwidget)
        self.findDupButton.setObjectName("findDupButton")
        self.gridLayout.addWidget(self.findDupButton, 1, 6, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 906, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        self.MyMessage = QtWidgets.QLabel()
        MainWindow.setStatusBar(self.statusbar)
        self.statusbar.addPermanentWidget(self.MyMessage)

        self.treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeWidget.customContextMenuRequested.connect(self.menuContextTree)

        self.lockIcon = QtGui.QIcon("lock.ico")
        self.unlockIcon = QtGui.QIcon("unlock.ico")
        self.starIcon = QtGui.QIcon("star.ico")
        self.passIcon = QtGui.QIcon("Iconsmind-Outline-Yes.ico")
        self.failIcon = QtGui.QIcon("error.ico")
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

#        delegate = AlignDelegate(self.treeWidget)
#        self.treeWidget.setItemDelegateForColumn(0, delegate)

        self.cloneBtn.clicked.connect(self.unselectClones)
        self.expColBtn.clicked.connect(self.expColTree)
        self.parentBtn.setChecked(True)
        self.groupMode = 'parent'
        self.parentBtn.toggled.connect(self.toggleParentMode)
        self.titleBtn.toggled.connect(self.toggleParentMode)
        self.clearSearchBtn.clicked.connect(self.clearSearch)
        self.uncheckedBtn.clicked.connect(self.toggleUncheckedHidden)
        self.findDupButton.clicked.connect(self.findDuplicates)

        self.treeWidget.itemChanged[QTreeWidgetItem, int].connect(self.treeItemChanged)

#        self.treeWidget.itemSelectionChanged.connect(self.treeItemSelected)
        
        menubar = self.menuBar()
        style = self.style()
        icon = QtGui.QIcon(style.standardIcon(getattr(QStyle, 'SP_BrowserStop')))
        exitAct = QAction(icon, 'Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.closeProgram)

        # icon = QtGui.QIcon(style.standardIcon(getattr(QStyle, 'SP_DialogOpenButton')))
        # loadAct = QAction(icon, 'Load', self)
        # loadAct.setShortcut('Ctrl+L')
        # loadAct.setStatusTip('Load File')
        # loadAct.triggered.connect(lambda: self.loadTree(self.currentDisplay, self.groupMode))

        icon = QtGui.QIcon(style.standardIcon(getattr(QStyle, 'SP_DialogSaveButton')))
        
        self.saveAct = QAction(icon, 'Save', self)
        self.saveAct.setShortcut('Ctrl+S')
        self.saveAct.setStatusTip('Save File')
        self.saveAct.triggered.connect(self.saveChangedLists)
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
#        fileMenu.addAction(loadAct)
        fileMenu.addAction(self.saveAct)
        fileMenu.addAction(findAct)
        fileMenu.addAction(configAct)
        fileMenu.addAction(exitAct)
        fileMenu.aboutToShow.connect(self.updateFileMenu)

        selFailedAct = QAction(icon, 'Select Failed', self)
        selFailedAct.setShortcut('Ctrl+B')
        selFailedAct.setStatusTip('Select Failed')
        selFailedAct.triggered.connect(lambda: self.selectByStatus('fail'))

        selPassedAct = QAction(icon, 'Select Passed', self)
        selPassedAct.setShortcut('Ctrl+G')
        selPassedAct.setStatusTip('Select Passed')
        selPassedAct.triggered.connect(lambda: self.selectByStatus('pass'))

        editMenu = menubar.addMenu('&Edit')
        editMenu.addAction(selFailedAct)
        editMenu.addAction(selPassedAct)

        self.treeWidget.setSortingEnabled(True)
        self.retranslateUi()

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # for i in self.dispDict.keys():
        #     print(i)
        #     for r in self.dispDict[i].romDict.keys():
        #         if self.dispDict[i].romDict[r].favorite == 'Y':
        #             print('   '+r)

    def selectByStatus(self, status):
        self.treeWidget.setFocus()
        root = self.treeWidget.invisibleRootItem()
        titleCount = root.childCount()
        for idx in range(titleCount):
            item = root.child(idx)
            if not item.isHidden():
                for cIdx in range(item.childCount()):
                    child = item.child(cIdx)
                    if not child.isHidden():
                        if self.dispDict[self.currentDisplay].romDict[child.text(self.col_rom)].status == status:
                            child.setSelected(True)
                        else:
                            child.setSelected(False)

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
                        if key == 'executable':
                            self.mameCfg.executable = val
                        line = fp.readline()
        except Exception as mameCfgExcept:
            traceback.print_exc()
            raise mameCfgExcept

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
            with open(fileToOpen, "r") as amConfig:
                line = amConfig.readline()
                while line:
                    cfgList.append(line)
                    line = amConfig.readline()
            for i, line in enumerate(cfgList):
                lvl, dispKey, dispVal = getCfgLineKeyVal(line)
                if lvl == 0 and dispKey == 'display':
                    displayCfg = recordtype('displayCfg', [('cfgDict', {}),
                                                           ('filterDict', {}),
                                                           ('romDict', {}),
                                                           ('favList', []),
                                                           ('dataChanged', False)
                                                           ])
                    displayCfg.cfgDict = dict()
                    displayCfg.romDict = dict()
                    displayCfg.favList = list()
                    displayCfg.cfgDict['validateExe'] = 'Unknown'
                    dispDict[dispVal] = displayCfg

                    i = loadDisplayCfg(cfgList, displayCfg, i)
        else:
            showMsg('Error',
                    'Unable to find AttractMode config file.  Please go to preferences and select the AttractMode '
                    'directory and ensure a config file exists')
        return dispDict

    def get_version_number(self, filename):
        try:
            info = win32api.GetFileVersionInfo(filename, "\\")
            ms = info['FileVersionMS']
            ls = info['FileVersionLS']
            return str(win32api.HIWORD(ms))+'.'+str(win32api.LOWORD(ms))
        except:
            return "Unknown version"

    def getFileDescription(self, windows_exe):
        try:
            language, codepage = win32api.GetFileVersionInfo(windows_exe, '\\VarFileInfo\\Translation')[0]
            stringFileInfo = u'\\StringFileInfo\\%04X%04X\\%s' % (language, codepage, "FileDescription")
            description = win32api.GetFileVersionInfo(windows_exe, stringFileInfo)
        except:
            description = "unknown"

        return description

    def getMameCfgExeVersion(self, mameExe, mameDisp):
        if mameExe != '':
            if mameExe.find('.exe') == -1:
                mameExe = mameExe + '.exe'
            if os.path.exists(os.path.join(mameExe)) and self.getFileDescription(mameExe) == 'MAME':
                mameVersionText = getMameVersion(mameExe)
                versionWords = [item.strip(' )').upper() for item in mameVersionText.split('(')]

                if len(versionWords) > 1:
                    if versionWords[1][0:4] == 'MAME':
                        print('Mame.cfg: Found Mame ' + self.mameCfg.executable + ' version: ' + versionWords[0])
                        if mameDisp.cfgDict['validateExe'] == 'Unknown':
                            mameDisp.cfgDict['validateExe'] = mameExe
                    else:
                        print('Mame.cfg: Non-Mame executable found (' + mameExe + ') version: '
                              + versionWords[0])
                    return versionWords[0]
            else:
                print('Executable in mame.cfg ('+mameExe+') does not appear to be a MAME build')
        return ''

    def getPrefsExeVersion(self, mameExe, mameDisp):
        if mameExe != '' and self.getFileDescription(mameExe) == 'MAME':
            self.configUi.mameExe.setText(mameExe)
            mameVersionText = getMameVersion(mameExe)
            versionWords = [item.strip(' )').upper() for item in mameVersionText.split('(')]

            if len(versionWords) > 1 and len(versionWords[1]) >= 4 and versionWords[1][0:4] == 'MAME':
                print('Preferences: Found Mame ' + self.configData.mameExe + ' version: ' + versionWords[0])
                mameDisp.cfgDict['validateExe'] = self.configData.mameExe
                return versionWords[0]
            else:
                print('Executable is not an official MAME build')
        else:
            print('Executable is not a MAME build')
        return ''

    def printDispCfg(self, pDisplay):
        disp = self.dispDict[pDisplay]

        print('\n--------------- '+pDisplay+' ---------------\n')
        for i in disp.cfgDict.items():
            print('{} = {}'.format(i[0], i[1]))

        for fName in disp.filterDict.keys():
            print('filter='+fName)
            for rule in disp.filterDict[fName]:
                print(' -- '+rule)

    def loadAmConfigFile(self):
        if os.path.exists(self.configfile):
            self.configData.loadJSON(self.configfile)
            self.configUi.amDir.setText(self.configData.amDir)
            self.dispDict = self.loadAmConfig(os.path.join(self.configData.amDir, "attract.cfg"))

            if 'Mame' in self.dispDict.keys():
                mameDisp = self.dispDict['Mame']
                self.loadMameCfg()
                prefsMameVersion = self.getPrefsExeVersion(self.configData.mameExe, mameDisp)
                mameCfgMameVersion = self.getMameCfgExeVersion(self.mameCfg.executable, mameDisp)

                if prefsMameVersion != '' and mameCfgMameVersion != '' and prefsMameVersion != mameCfgMameVersion:
                    print('Mame version mismatch between preferences Mame exe and mame.cfg exe ({} vs. {})'.
                          format(prefsMameVersion, mameCfgMameVersion))

                print('Validation exe: '+mameDisp.cfgDict['validateExe'])

    def showPreferences(self):
        currAmDir = self.configUi.amDir.text()
        currMameExe = self.configUi.mameExe.text()

        self.configDialog.show()
        rsp = self.configDialog.exec_()
        if rsp == QDialog.Accepted:
            if (self.configData.amDir != self.configUi.amDir.text() or
                    self.configData.mameExe != self.configUi.mameExe.text()):
                loadConfig = True
                self.configData.amDir = self.configUi.amDir.text()
                self.configData.mameExe = self.configUi.mameExe.text()
                self.configData.saveJSON(self.configfile)
            else:
                loadConfig = False
            if loadConfig:
                self.loadAmConfigFile()
        else:
            self.configUi.amDir.setText(currAmDir)
            self.configUi.mameExe.setText(currMameExe)
        return rsp

    def dataChanged(self):
        if len(self.dispDict) > 0:
            for d in self.dispDict.keys():
                if self.dispDict[d].dataChanged:
                    return True
        return False

    def getChangedDispList(self):
        changedDispList = list()
        if self.dataChanged():
            for d in self.dispDict.keys():
                if self.dispDict[d].dataChanged:
                    changedDispList.append(d)
        return changedDispList

    def ignoreUnsavedChangesWarning(self):
        ignore = True
        dList = self.getChangedDispList()
        if len(dList) > 0:
            dText = ''
            for d in dList:
                dText = dText + d + '\n'
            reply = QMessageBox.question(self,
                                         "Unsaved Changes",
                                         "There are unsaved changes in the following lists:\n" +
                                         dText +
                                         "Are you sure you want to exit?",
                                         QMessageBox.Yes,
                                         QMessageBox.No)
            if reply != QMessageBox.Yes:
                ignore = False
        return ignore

    def loadDisplay(self):
        action = self.sender()
        if action.text() != self.currentDisplay:
            self.loadTree(action.text(), self.groupMode)
            self.currentDisplay = action.text()

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
        MainWindow.setWindowTitle(_translate(   "MainWindow", self.windowTitle))
        self.cloneBtn.setText(_translate("MainWindow", "Uncheck Clones"))
        self.treeWidget.setSortingEnabled(True)
        self.clearSearchBtn.setText(_translate("MainWindow", "Clear Search"))
        self.expColBtn.setText(_translate("MainWindow", "Expand All"))
        self.label.setText(_translate("MainWindow", "Group Mode"))
        self.parentBtn.setText(_translate("MainWindow", "Parent"))
        self.titleBtn.setText(_translate("MainWindow", "Title"))
        self.uncheckedBtn.setText(_translate("MainWindow", "Hide Unchecked"))
        self.findDupButton.setText(_translate("MainWindow", "Find Duplicates"))

    def updateFileMenu(self):
        if self.dataChanged():
            self.saveAct.setEnabled(True)

    def treeItemChanged(self, item, column):
        if not self.treeLoading:
            self.dispDict[self.currentDisplay].dataChanged = True
            MainWindow.setWindowTitle(QtCore.QCoreApplication.translate("MainWindow", self.windowTitle+' *'))
            if item.parent():
                romName = item.text(self.col_rom)
                newLine = self.dispDict[self.currentDisplay].romDict[romName].lstLine

#                if column == self.col_status:
#                    status = item.text(self.col_status)
#                    self.dispDict[self.currentDisplay].romDict[romName].status = status

                if column == self.col_name:
                    if item.checkState(0) == QtCore.Qt.Checked:
                        newLine = self.removeLineFieldVal(newLine, 'Extra', 'excluded')
                        self.dispDict[self.currentDisplay].romDict[romName].excluded = 'N'
                    else:
                        newLine = self.addLineFieldVal(newLine, 'Extra', 'excluded')
                        self.dispDict[self.currentDisplay].romDict[romName].excluded = 'Y'

                self.dispDict[self.currentDisplay].romDict[romName].lstLine = newLine

    def toggleParentMode(self):
        radioButton = self.sender()
        if radioButton.isChecked():
            if radioButton.objectName() == 'parentBtn':
                self.groupMode = 'parent'
            elif radioButton.objectName() == 'titleBtn':
                self.groupMode = 'title'
            self.loadTree(self.currentDisplay, self.groupMode)
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
                newLine = self.dispDict[self.currentDisplay].romDict[tree_item.text(self.col_rom)].lstLine
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
                if (column_name == 'locked'   and self.dispDict[self.currentDisplay].romDict[rom_name].locked   == col_value or
                        column_name == 'favorite' and self.dispDict[self.currentDisplay].romDict[rom_name].favorite == col_value or
                        column_name == 'status'   and self.dispDict[self.currentDisplay].romDict[rom_name].status   == col_value):
                    value_count += 1
        return item_count, value_count

    def lockItem(self, tree_item):
        if tree_item.parent():
            tree_item.setIcon(0, self.lockIcon)
            self.dispDict[self.currentDisplay].romDict[tree_item.text(self.col_rom)].locked = 'Y'

    def unlockItem(self, tree_item):
        if tree_item.parent():
            tree_item.setIcon(0, self.unlockIcon)
            self.dispDict[self.currentDisplay].romDict[tree_item.text(self.col_rom)].locked = 'N'

    def setSelectedLockStatus(self, status):
        selected_items = self.treeWidget.selectedItems()
        for tree_item in selected_items:
            if tree_item.parent():
                if status == 'lock':
                    self.lockItem(tree_item)
                elif status == 'unlock':
                    self.unlockItem(tree_item)
                elif status == 'toggle':
                    if self.dispDict[self.currentDisplay].romDict[tree_item.text(self.col_rom)].locked == 'Y':
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
        rom_name = tree_item.text(self.col_rom)
        if tree_item.parent() and self.dispDict[self.currentDisplay].romDict[rom_name].locked == 'N':
            tree_item.setIcon(self.col_favorite, self.starIcon)
            self.dispDict[self.currentDisplay].romDict[rom_name].favorite = 'Y'
            if rom_name not in self.dispDict[self.currentDisplay].favList:
                self.dispDict[self.currentDisplay].favList.append(rom_name)

    def unfavoriteItem(self, tree_item):
        rom_name = tree_item.text(self.col_rom)
        if tree_item.parent() and self.dispDict[self.currentDisplay].romDict[rom_name].locked == 'N':
            tree_item.setIcon(self.col_favorite, self.blankIcon)
            self.dispDict[self.currentDisplay].romDict[rom_name].favorite = 'N'
            if rom_name in self.dispDict[self.currentDisplay].favList:
                self.dispDict[self.currentDisplay].remove(rom_name)

    def setSelectedFavoriteStatus(self, status):
        selected_items = self.treeWidget.selectedItems()
        for tree_item in selected_items:
            if tree_item.parent():
                if status == 'favorite':
                    self.favoriteItem(tree_item)
                elif status == 'unfavorite':
                    self.unfavoriteItem(tree_item)
                elif status == 'toggle':
                    if self.dispDict[self.currentDisplay].romDict[tree_item.text(self.col_rom)].favorite == 'Y':
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
                action = menu.addAction("Remove "+name+" from favorites")
                action.triggered.connect(functools.partial(self.setSelectedFavoriteStatus, 'unfavorite'))

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
                if (status == 'selected'
                    or status == 'passed' and self.dispDict[self.currentDisplay].romDict[tree_item.text(self.col_rom)].status == 'pass'
                        or status == 'failed' and self.dispDict[self.currentDisplay].romDict[tree_item.text(self.col_rom)].status == 'fail'):
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
                action.triggered.connect(functools.partial(self.validateSelected, 'selected'))
            else:
                if self.dispDict[self.currentDisplay].cfgDict['validateExe'] != 'Unknown':
                    action = menu.addAction("Validate failed")
                    action.triggered.connect(functools.partial(self.validateSelected, 'failed'))
                    action = menu.addAction("Validate passed")
                    action.triggered.connect(functools.partial(self.validateSelected, 'passed'))
                    action = menu.addAction("Validate selected")
                    action.triggered.connect(functools.partial(self.validateSelected, 'selected'))

    def setSelectedCheckStatus(self, status):
        selected_items = self.treeWidget.selectedItems()
        for tree_item in selected_items:
            if tree_item.parent() and self.dispDict[self.currentDisplay].romDict[tree_item.text(self.col_rom)].locked == 'N':
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
        except Exception as expColTreeExcept:
            traceback.print_exc()
            raise expColTreeExcept
            
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

    def saveTag(self, listName):
        try:
            if listName != '' and len(self.dispDict[listName].romDict) > 0:
                fileToOpen = os.path.join(self.configData.amDir, "romlists\\"+listName+".tag")
                with open(fileToOpen, "w") as of:
                    for romItem in sorted(self.dispDict[listName].romDict.values(), key=lambda kv: kv.title):
                        if romItem.favorite == 'Y':
                            wordList = romItem.lstLine.strip('\n\r').split(';')
                            rom_name = wordList[self.lineHeaderDict['Name']]
                            of.write(rom_name+'\n')
        except Exception as saveTagExcept:
            traceback.print_exc()
            raise saveTagExcept

    def saveAlm(self, listName):
        if listName != '' and len(self.dispDict[listName].romDict) > 0:
            fileToOpen = os.path.join(self.configData.amDir, "romLists\\"+listName+".alm")
            with open(fileToOpen, "w") as of:
                of.write('#Name;Excluded;Locked;Status\n')
                for romItem in sorted(self.dispDict[listName].romDict.values(), key=lambda kv: kv.title):
                    if romItem.lstLine == '':
                        continue
                    wordList = romItem.lstLine.strip('\n\r').split(';')
                    rom = wordList[self.lineHeaderDict['Name']]
                    if self.dispDict[listName].romDict[rom].locked == 'Y' or self.dispDict[listName].romDict[rom].excluded == 'Y' or\
                            self.dispDict[listName].romDict[rom].status != '':
                        newLine = rom
                        if self.dispDict[listName].romDict[rom].excluded == 'Y':
                            newLine += ';Y'
                        else:
                            newLine += ';N'
                        if self.dispDict[listName].romDict[rom].locked == 'Y':
                            newLine += ';Y'
                        else:
                            newLine += ';N'
                        if self.dispDict[listName].romDict[rom].status != '':
                            newLine += ';'+self.dispDict[listName].romDict[rom].status
                        else:
                            newLine += ';unknown'
                        of.write(newLine+'\n')

    def saveChangedLists(self):
        try:
            for d in self.dispDict.keys():
                if self.dispDict[d].dataChanged and len(self.dispDict[d].romDict) > 0:
                    fileToOpen = os.path.join(self.configData.amDir, "romlists\\"+d+".txt")
                    with open(fileToOpen, "w") as of:
                        of.write(self.fileHeader)
                        for romItem in sorted(self.dispDict[d].romDict.values(), key=lambda kv: kv.title):
                            of.write(romItem.lstLine+'\n')
                    self.saveAlm(d)
                    self.saveTag(d)
                    self.dispDict[d].dataChanged = False
                    self.saveAct.setEnabled(False)
                    print('Saved '+d+' to '+fileToOpen)
            MainWindow.setWindowTitle(QtCore.QCoreApplication.translate("MainWindow", self.windowTitle))

        except Exception as saveListExcept:
            traceback.print_exc()
            raise saveListExcept

    def addParent(self, newTitle, romname, emu, category):
        gameIdx = self.treeWidget.topLevelItemCount()
        self.parentCloneOfDict[romname] = gameIdx
        # if romname in self.dispDict[self.currentDisplay].romDict:
        #     self.dispDict[self.currentDisplay].romDict[romname].treeIdx = gameIdx
        # else:
        #     self.dispDict[self.currentDisplay].romDict[romname] = self.romItem(treeIdx=gameIdx)
        if newTitle not in self.parentTitleDict:
            self.parentTitleDict[newTitle] = gameIdx
        self.treeWidget.addTopLevelItem(QTreeWidgetItem(gameIdx))
        treeItem = self.treeWidget.topLevelItem(gameIdx)
        treeItem.setFlags(int(treeItem.flags()) | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsTristate)
        treeItem.setText(self.col_name, newTitle)
        treeItem.setText(self.col_emulator, emu)
        treeItem.setText(self.col_category, category)
        return treeItem

    def addChild(self, treeItem, newTitle, variation, romname, cloneOf, status, category):

        childItem = QTreeWidgetItem()

        if romname in self.dispDict[self.currentDisplay].romDict and self.dispDict[self.currentDisplay].romDict[romname].excluded == 'Y':
            childItem.setCheckState(0, Qt.Unchecked)
        else:
            childItem.setCheckState(0, Qt.Checked)

        childItem.setText(self.col_name,        newTitle)
        childItem.setText(self.col_variation,   variation)
        childItem.setText(self.col_rom,         romname)
        childItem.setText(self.col_cloneof,     cloneOf)
#        childItem.setText(self.col_status,      status)
        if status == 'pass':
            childItem.setIcon(self.col_status, self.passIcon)
        else:
            childItem.setIcon(self.col_status, self.failIcon)

#        if romname in self.dispDict[self.currentDisplay].favList:
        if self.dispDict[self.currentDisplay].romDict[romname].favorite == 'Y':
            childItem.setIcon(self.col_favorite, self.starIcon)
#            self.dispDict[self.currentDisplay].romDict[childItem.text(self.col_rom)].favorite = 'Y'
        else:
            childItem.setIcon(self.col_favorite, self.blankIcon)
#            self.dispDict[self.currentDisplay].romDict[childItem.text(self.col_rom)].favorite = 'N'

        childItem.setText(self.col_category, category)

        treeItem.insertChild(treeItem.childCount(), childItem)
        childItem = treeItem.child(treeItem.childCount()-1)

        # Has to be after child is added because only child items can be locked
        if romname in self.dispDict[self.currentDisplay].romDict and self.dispDict[self.currentDisplay].romDict[romname].locked == 'Y':
            self.lockItem(childItem)
        else:
            self.unlockItem(childItem)

    def showStatus(self):
        root = self.treeWidget.invisibleRootItem()
        titleCount = root.childCount()
        hiddenGroupCount = 0
        hiddenChildCount = 0

        for idx in range(titleCount):
            item = root.child(idx)
            if item.isHidden():
                hiddenGroupCount += 1
            for cIdx in range(item.childCount()):
                child = item.child(cIdx)
                if child.isHidden():
                    hiddenChildCount += 1

        if hiddenGroupCount > 0 or hiddenChildCount > 0:
            self.MyMessage.setText(
                "{} Groups ({} hidden) containing {} games ({} hidden)".
                    format(titleCount - hiddenGroupCount,
                           hiddenGroupCount,
                           len(self.dispDict[self.currentDisplay].romDict) - hiddenChildCount,
                           hiddenChildCount))
        else:
            self.MyMessage.setText(
                "{} Groups containing {} games".format(titleCount, len(self.dispDict[self.currentDisplay].romDict)))

    def loadTree(self, listName, mode):
        self.currentDisplay = listName

        if len(self.dispDict[self.currentDisplay].romDict) == 0:
            return

        self.treeWidget.clear()
        app.processEvents()
        
        self.treeWidget.setSortingEnabled(False)
        self.parentCloneOfDict.clear()
        self.parentTitleDict.clear()

        titleCol = self.lineHeaderDict['Title']
        cloneOfCol = self.lineHeaderDict['CloneOf']
        emuCol = self.lineHeaderDict['Emulator']
        catCol = self.lineHeaderDict['Category']

        d = QtWidgets.QDialog()
        dui = ProgressDialog(parent=self, flags=Qt.Dialog)
        dui.setupUi(d)
        d.show()
        dui.setProgressRange(1, len(self.dispDict[self.currentDisplay].romDict)*2)

        idx = 0
        self.treeLoading = True

        for level in ('parent', 'child'):
            for romname, romItem in self.dispDict[self.currentDisplay].romDict.items():
                line = romItem.lstLine
                if line.strip() == '':
                    continue
                try:
                    if dui.isCancelled():
                        break
                    wordlist = line.strip('\n\r').split(';')
                    cloneOf = wordlist[cloneOfCol]
                    title = wordlist[titleCol]
                    status = self.dispDict[self.currentDisplay].romDict[romname].status
                    newTitle, variation = getTitleVariation(title)
                    emu = wordlist[emuCol]
                    category = wordlist[catCol]

                    if mode == 'parent':
                        if level == 'parent':
                            if cloneOf == "":
                                treeItem = self.addParent(newTitle, romname, emu, category)
                                self.addChild(treeItem, newTitle, variation, romname, cloneOf, status, category)
                        else:
                            if cloneOf != "":
                                if cloneOf in self.parentCloneOfDict.keys():
                                    gameIdx = self.parentCloneOfDict[cloneOf]
                                    treeItem = self.treeWidget.topLevelItem(gameIdx)
                                else:
                                    # Parent ROM not found, create dummy parent using cloneOf value
                                    treeItem = self.addParent(cloneOf, cloneOf, emu, category)
                                self.addChild(treeItem, newTitle, variation, romname, cloneOf, status, category)

                    elif mode == 'title':
                        if level == 'parent':
                            if newTitle not in self.parentTitleDict:
                                self.addParent(newTitle, romname, emu, category)
                        else:
                            gameIdx = self.parentTitleDict[newTitle]
                            treeItem = self.treeWidget.topLevelItem(gameIdx)
                            self.addChild(treeItem, newTitle, variation, romname, cloneOf, status, category)
                    idx += 1
                    dui.setProgressValue(idx)
                    if idx % 100 == 0:
                        app.processEvents()
                except Exception as loadTreeExcept:
                    traceback.print_exc()
                    raise loadTreeExcept
        self.treeLoading = False
        self.treeWidget.setSortingEnabled(True)
        self.showStatus()
        self.treeWidget.sortByColumn(self.col_name, Qt.AscendingOrder)
        self.treeWidget.sortByColumn(self.col_cloneof, Qt.AscendingOrder)
        self.treeWidget.resizeColumnToContents(self.col_name)
        self.treeWidget.resizeColumnToContents(self.col_status)
        self.treeWidget.expandAll()
        self.expColBtn.setText("Collapse")
        app.processEvents()
        print('Loaded tree from '+listName)

    def loadList(self, listName):
        try:
#            self.printDispCfg(listName)

            fileToOpen = os.path.join(self.configData.amDir, "romlists\\" + listName + ".txt")
            if os.path.exists(fileToOpen):
                self.dispDict[listName].dataChanged = False
                self.treeWidget.clear()
                self.dispDict[listName].romDict.clear()
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
                        if line.strip() == '':
                            line = fp.readline()
                            continue
                        wordlist = line.strip('\n\r').split(';')
                        romname = wordlist[self.lineHeaderDict['Name']]
                        emuname = wordlist[self.lineHeaderDict['Emulator']]
                        gameTitle   = wordlist[self.lineHeaderDict['Title']]
                        self.dispDict[listName].romDict[romname] = self.romItem(lstLine=line.strip('\n'))
                        self.dispDict[listName].romDict[romname].title = gameTitle
                        self.dispDict[listName].romDict[romname].favorite = 'N'
                        if emuname not in self.emuDict.keys():
                            self.emuDict[emuname] = 'None'
                        line = fp.readline()
#                    self.addMenu('Emulator', self.emuDict, self.loadDisplay)

                if self.firstLoad:
                    bkpFile = os.path.join(fileToOpen+".bkp")
                    with open(bkpFile, "w") as of:
                        of.write(self.fileHeader)
                        for romItem in self.dispDict[listName].romDict.values():
                            of.write(romItem.lstLine+'\n')

                fileToOpen = os.path.join(self.configData.amDir, "romlists\\" + listName + ".tag")
                if os.path.exists(fileToOpen):
                    with open(fileToOpen) as fp:
                        line = fp.readline()
                        while line:
                            fav_rom = line.strip('\n\r')
                            self.dispDict[listName].favList.append(fav_rom)
                            if fav_rom in self.dispDict[listName].romDict:
                                self.dispDict[listName].romDict[fav_rom].favorite = 'Y'
                            line = fp.readline()

                if self.firstLoad:
                    bkpFile = os.path.join(fileToOpen+".bkp")
                    with open(bkpFile, "w") as of:
                        for fav_rom in self.dispDict[listName].favList:
                            of.write(fav_rom+'\n')


                fileToOpen = os.path.join(self.configData.amDir, "romlists\\" + listName + ".alm")

                if os.path.exists(fileToOpen):
                    with open(fileToOpen) as fp:
                        # Read in the header
                        #TODO actually use header
                        line = fp.readline().strip('\n')
                        line = fp.readline().strip('\n')
                        while line:
                            almFields = line.split(';')
                            if almFields[0] in self.dispDict[listName].romDict:
                                self.dispDict[listName].romDict[almFields[0]].excluded = almFields[1]
                                self.dispDict[listName].romDict[almFields[0]].locked = almFields[2]
                                self.dispDict[listName].romDict[almFields[0]].status = almFields[3]
                            else:
                                self.dispDict[listName].romDict[almFields[0]] = self.romItem(excluded=almFields[1],
                                                                          locked=almFields[2],
                                                                          status=almFields[3])
                            line = fp.readline().strip('\n')

            print('Loaded list '+listName)
        except Exception as loadListExcept:
            traceback.print_exc()
            raise loadListExcept

    def validateRom(self, romname):
        if self.dispDict['Mame'].cfgDict['validateExe'] != 'Unknown':
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
        else:
            return None

    def validateTreeItem(self, treeItem):
        try:
            rom_name = treeItem.text(self.col_rom)
            return_code = self.validateRom(rom_name)
            if return_code != 0:
                treeItem.setCheckState(0, Qt.Unchecked)
                status = 'fail'
                treeItem.setIcon(self.col_status, self.failIcon)
            else:
                status = 'pass'
                treeItem.setIcon(self.col_status, self.passIcon)

            self.dispDict[self.currentDisplay].romDict[rom_name].status = status
            return status

        except Exception as validateTreeItemExcept:
            traceback.print_exc()
            raise validateTreeItemExcept

#    def msgbtn(self, i):
#        print("Button pressed is {}".format(i.text()))

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

                    for cIdx in range(item.childCount()):
                        child = item.child(cIdx)
                        if child.checkState(0) == QtCore.Qt.Checked:
                            child.setHidden(False)

        except Exception as findDuplicatesExcept:
            traceback.print_exc()
            raise findDuplicatesExcept

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
                                    and child.text(self.col_cloneof) == parentRom
                                    and self.dispDict[self.currentDisplay].romDict[child.text(self.col_rom)].locked == 'N'):
                                child.setCheckState(0, Qt.Unchecked)
#            self.findDuplicates()
        except Exception as unselectClonesExcept:
            traceback.print_exc()
            raise unselectClonesExcept

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

        except Exception as setUnceckedHiddenExcept:
            traceback.print_exc()
            raise setUnceckedHiddenExcept

    def toggleUncheckedHidden(self):
        if self.uncheckedBtn.text() == 'Hide Unchecked':
            self.setUncheckedHidden(True)
            self.uncheckedBtn.setText('Show Unchecked')
        else:
            self.setUncheckedHidden(False)
            self.uncheckedBtn.setText('Hide Unchecked')
        self.showStatus()

    def applyUncheckedHidden(self):
        if self.uncheckedBtn.text() == 'Hide Unchecked':
            self.setUncheckedHidden(False)
        else:
            self.setUncheckedHidden(True)

    def clearSearch(self):
        self.setTreeHidden(False)
        self.applyUncheckedHidden()
        self.findField = ''
        self.findText = ''
        self.searchOn = False
        self.showStatus()

    def loadAllDisplays(self):
        rsp = QDialog.Accepted
        while rsp == QDialog.Accepted and len(self.dispDict) == 0:
            rsp = self.showPreferences()
        if len(self.dispDict) > 0:
            for disp in self.dispDict.keys():
                self.loadList(disp)
            self.firstLoad = False
            self.loadTree(list(self.dispDict.keys())[0], 'parent')
            self.addMenu('Display', self.dispDict, self.loadDisplay)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    MainWindow = Ui_MainWindow()
    MainWindow.setupUi()
    MainWindow.show()
    MainWindow.loadAmConfigFile()
    MainWindow.loadAllDisplays()

    try:
        sys.exit(app.exec_())
    except Exception as e:
        traceback.print_exc()
        raise e
