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
    newTitle = newTitle.split('/')[0].strip()
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


def newDisplayCfg(group_mode):
    displayCfg = recordtype('displayCfg', [('cfgDict', {}),
                                           ('filterDict', {}),
                                           ('romDict', {}),
                                           ('favList', []),
                                           ('dataChanged', False),
                                           ('groupMode', ''),
                                           ('action', None),
                                           ('clonesExist', False)
                                           ])
    displayCfg.cfgDict = dict()
    displayCfg.romDict = dict()
    displayCfg.favList = list()
    displayCfg.cfgDict['validateExe'] = 'Unknown'
    displayCfg.groupMode = group_mode

    return displayCfg


def loadAmConfig(fileToOpen):
    dispDict = dict()
    if os.path.exists(fileToOpen):
        cfgList = list()
        with open(fileToOpen, "r") as amConfig:
            line = amConfig.readline()
            while line:
                cfgList.append(line)
                line = amConfig.readline()
        i = 0
        while i < len(cfgList):
            line = cfgList[i]
            lvl, dispKey, dispVal = getCfgLineKeyVal(line)
            if lvl == 0 and dispKey == 'display':
                displayCfg = newDisplayCfg('parent')
                if dispVal != 'Favorites':
                    dispDict[dispVal] = displayCfg

                i = loadDisplayCfg(cfgList, displayCfg, i)
            i = i+1
    else:
        showMsg('Error',
                'Unable to find AttractMode config file.  Please go to preferences and select the AttractMode '
                'directory and ensure a config file exists')
    return dispDict


def get_version_number(filename):
    try:
        info = win32api.GetFileVersionInfo(filename, "\\")
        ms = info['FileVersionMS']
        # ls = info['FileVersionLS']
        return str(win32api.HIWORD(ms))+'.'+str(win32api.LOWORD(ms))
    finally:
        return "Unknown version"


def getFileDescription(windows_exe):
    try:
        language, codepage = win32api.GetFileVersionInfo(windows_exe, '\\VarFileInfo\\Translation')[0]
        stringFileInfo = u'\\StringFileInfo\\%04X%04X\\%s' % (language, codepage, "FileDescription")
        description = win32api.GetFileVersionInfo(windows_exe, stringFileInfo)
    except:
        description = "unknown"

    return description


def getMameExeVersion(mameSrc, mameExe, mameDisp):
    if mameExe != '':
        if mameExe.find('.exe') == -1:
            mameExe = mameExe + '.exe'
        if os.path.exists(os.path.join(mameExe)) and getFileDescription(mameExe) == 'MAME':
            mameVersionText = getMameVersion(mameExe)
            versionWords = [item.strip(' )').upper() for item in mameVersionText.split('(')]

            if len(versionWords) > 1:
                if versionWords[1][0:4] == 'MAME':
                    print(mameSrc+': Found Mame ' + mameExe + ' version: ' + versionWords[0])
                    if mameDisp.cfgDict['validateExe'] == 'Unknown':
                        mameDisp.cfgDict['validateExe'] = mameExe
                else:
                    print(mameSrc+': Non-Mame executable found (' + mameExe + ') version: ' + versionWords[0])
                return versionWords[0]
        else:
            print(mameSrc+': Executable ('+mameExe+') does not appear to be a MAME build')
    return ''


class Ui_MainWindow(QMainWindow):
    fileHeader = str()
    romItem = recordtype('romItem', [('lineDict', {})])
    listHeaderIdx = dict()
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
    prefs = AmConfig()
    prefsFile = 'AttractModeListMgr.cfg'
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
        self.clearSearchBtn = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.clearSearchBtn.sizePolicy().hasHeightForWidth())
        self.clearSearchBtn.setSizePolicy(sizePolicy)
        self.clearSearchBtn.setObjectName("clearSearchBtn")
        self.gridLayout.addWidget(self.clearSearchBtn, 1, 10, 1, 1)
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
        self.gridLayout.addWidget(self.treeWidget, 4, 0, 1, 11)
        self.cloneBtn = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cloneBtn.sizePolicy().hasHeightForWidth())
        self.cloneBtn.setSizePolicy(sizePolicy)
        self.cloneBtn.setObjectName("cloneBtn")
        self.gridLayout.addWidget(self.cloneBtn, 1, 7, 1, 1)
        self.uncheckedBtn = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uncheckedBtn.sizePolicy().hasHeightForWidth())
        self.uncheckedBtn.setSizePolicy(sizePolicy)
        self.uncheckedBtn.setObjectName("uncheckedBtn")
        self.gridLayout.addWidget(self.uncheckedBtn, 1, 6, 1, 1)
        self.expColBtn = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.expColBtn.sizePolicy().hasHeightForWidth())
        self.expColBtn.setSizePolicy(sizePolicy)
        self.expColBtn.setObjectName("expColBtn")
        self.gridLayout.addWidget(self.expColBtn, 1, 5, 1, 1)
        self.findDupButton = QtWidgets.QPushButton(self.centralwidget)
        self.findDupButton.setObjectName("findDupButton")
        self.gridLayout.addWidget(self.findDupButton, 1, 9, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 8, 1, 1)
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QtCore.QSize(300, 30))
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
        self.parentBtn.setGeometry(QtCore.QRect(80, 6, 56, 17))
        self.parentBtn.setObjectName("parentBtn")
        self.titleBtn = QtWidgets.QRadioButton(self.frame)
        self.titleBtn.setGeometry(QtCore.QRect(160, 6, 44, 17))
        self.titleBtn.setObjectName("titleBtn")
        self.noneBtn = QtWidgets.QRadioButton(self.frame)
        self.noneBtn.setGeometry(QtCore.QRect(230, 6, 61, 17))
        self.noneBtn.setObjectName("noneBtn")
        self.gridLayout.addWidget(self.frame, 1, 1, 1, 4)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 906, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.MyMessage = QtWidgets.QLabel()
        MainWindow.setStatusBar(self.statusbar)
        self.statusbar.addPermanentWidget(self.MyMessage)

        self.treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeWidget.customContextMenuRequested.connect(self.menuContextTree)

        self.lockIcon = QtGui.QIcon("icons\\lock.ico")
        self.unlockIcon = QtGui.QIcon("icons\\unlock.ico")
        self.starIcon = QtGui.QIcon("icons\\star.ico")
        self.openStarIcon = QtGui.QIcon("icons\\openStar.ico")
        self.passIcon = QtGui.QIcon("icons\\Iconsmind-Outline-Yes.ico")
        self.failIcon = QtGui.QIcon("icons\\error.ico")
        self.searchIcon = QtGui.QIcon("icons\\Search2.ico")
        self.gearIcon = QtGui.QIcon("icons\\Gear.ico")
        self.mergeIcon = QtGui.QIcon("icons\\Merge.ico")
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
        self.column_headers = ['Title', 'Favorite', 'Status', 'Variation', 'Rotation', 'Category', 'Emulator',
                               'Control', 'Buttons', 'Players', 'Name', 'CloneOf',
                               'Status (pass or fail)', 'Favorite (Y or N)', 'Locked (Y or N)']
        self.col_idx = {}

        self.headerView = QtWidgets.QHeaderView(Qt.Horizontal)
        self.headerView.setSectionsMovable(True)
        self.treeWidget.setHeader(self.headerView)

        for idx, header in enumerate(self.column_headers):
            self.treeWidget.headerItem().setText(idx, header)
            self.col_idx[header] = idx

        self.treeWidget.hideColumn(self.col_idx['Status (pass or fail)'])
        self.treeWidget.hideColumn(self.col_idx['Favorite (Y or N)'])
        self.treeWidget.hideColumn(self.col_idx['Locked (Y or N)'])

        # print(self.headerView.visualIndex(1))
        # delegate = AlignDelegate(self.treeWidget)
        # self.treeWidget.setItemDelegateForColumn(0, delegate)

        self.cloneBtn.clicked.connect(self.unselectClones)
        self.expColBtn.clicked.connect(self.expColTree)
        self.parentBtn.setChecked(True)
        self.parentBtn.toggled.connect(self.toggleParentMode)
        self.titleBtn.toggled.connect(self.toggleParentMode)
        self.noneBtn.toggled.connect(self.toggleParentMode)
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
        # loadAct.triggered.connect(lambda: self.loadTree(self.currentDisplay,
        #   self.dispDict[self.currentDisplay].groupMode))

        self.saveIcon = QtGui.QIcon(style.standardIcon(getattr(QStyle, 'SP_DialogSaveButton')))
        
        self.saveAct = QAction(self.saveIcon, 'Save', self)
        self.saveAct.setShortcut('Ctrl+S')
        self.saveAct.setStatusTip('Save File')
        self.saveAct.triggered.connect(self.saveChangedDisplays)
        self.saveAct.setEnabled(False)

        # saveFavAct = QAction(icon, 'Save Favorites', self)
        # saveFavAct.setStatusTip('Save Favorites.txt')
        # saveFavAct.triggered.connect(lambda: self.saveDisplay('Favorites'))

        fileMenu = menubar.addMenu('&File')
        # fileMenu.addAction(loadAct)
        fileMenu.addAction(self.saveAct)
        # fileMenu.addAction(saveFavAct)
        # fileMenu.addAction(findAct)
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

        self.favoritesAct = QAction(self.mergeIcon, 'Merge Favorites', self)
        self.favoritesAct.setStatusTip('Copy favorites from all displays to the Favorites display')
        self.favoritesAct.triggered.connect(self.updateFavorites)

        editMenu = menubar.addMenu('&Edit')
        configAct = QAction(self.gearIcon, 'Preferences', self)
        configAct.setShortcut('Ctrl+P')
        configAct.setStatusTip('Set Preferences')
        configAct.triggered.connect(self.showPreferencesNoRsp)
        editMenu.addAction(configAct)

        findAct = QAction(self.searchIcon, 'Find', self)
        findAct.setShortcut('Ctrl+F')
        findAct.setStatusTip('Find')
        findAct.triggered.connect(self.showFindDlg)
        editMenu.addAction(findAct)

        favMenu = menubar.addMenu('&Favorites')
        favMenu.addAction(self.favoritesAct)
        # editMenu.addAction(selFailedAct)
        # editMenu.addAction(selPassedAct)

        self.treeWidget.setSortingEnabled(True)
        self.retranslateUi()

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # for i in self.dispDict.keys():
        #     print(i)
        #     for r in self.dispDict[i].romDict.keys():
        #         if self.dispDict[i].romDict[r].favorite == 'Y':
        #             print('   '+r)

    def selectByStatus(self, status):
        root = self.treeWidget.invisibleRootItem()
        titleCount = root.childCount()

        d = QtWidgets.QDialog()
        dui = ProgressDialog(parent=self, flags=Qt.Dialog)
        dui.setupUi(d)
        d.show()
        dui.setProgressRange(1, titleCount)

        for idx in range(titleCount):
            item = root.child(idx)
            if not item.isHidden():
                for cIdx in range(item.childCount()):
                    child = item.child(cIdx)
                    if not child.isHidden():
                        child.setSelected(self.getTreeItemLineDictVal(child, 'Status') == status)
                        dui.setProgressValue(idx + 1)
                        if idx%1000 == 0:
                            app.processEvents()

        dui.setProgressValue(titleCount + 1)
        self.treeWidget.setFocus()

    def loadMameCfg(self):
        try:
            fileToOpen = os.path.join(self.prefs.amDir, "emulators\\Mame.cfg")
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
#            name = item.text(self.col_idx['Title'])  # The text of the node.

        # Context menu
        menu = QtWidgets.QMenu()
        self.setFavoriteContextMenu(menu, point)
        if self.currentDisplay != 'Favorites':
            menu.addSeparator()
            self.setLockedContextMenu(menu, point)
            menu.addSeparator()
            self.setCheckedContextMenu(menu, point)
            menu.addSeparator()
            self.setValidateContextMenu(menu, point)

        menu.exec_(self.treeWidget.mapToGlobal(point))

    def setMenuIcons(self):
        for d in self.dispDict.keys():
            if d == self.currentDisplay:
                self.dispDict[d].action.setIcon(self.starIcon)
            else:
                self.dispDict[d].action.setIcon(self.blankIcon)

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
            dispAct.triggered.connect(functools.partial(connectAction, s))
            if menuName == 'Display':
                self.dispDict[s].action = dispAct

            dispMenu.addAction(dispAct)

    def printDispCfg(self, pDisplay):
        disp = self.dispDict[pDisplay]

        print('\n--------------- '+pDisplay+' ---------------\n')
        for i in disp.cfgDict.items():
            print('{} = {}'.format(i[0], i[1]))

        for fName in disp.filterDict.keys():
            print('filter='+fName)
            for rule in disp.filterDict[fName]:
                print(' -- '+rule)

    def loadPrefs(self):
        if os.path.exists(self.prefsFile):
            self.prefs.loadJSON(self.prefsFile)
            self.configUi.amDir.setText(self.prefs.amDir)
            if len(self.dispDict) == 0:
                self.dispDict = loadAmConfig(os.path.join(self.prefs.amDir, "attract.cfg"))

            if 'Mame' in self.dispDict.keys():
                mameDisp = self.dispDict['Mame']
                self.loadMameCfg()

                if self.prefs.mameExe != '':
                    self.configUi.mameExe.setText(self.prefs.mameExe)

                prefsMameVersion = getMameExeVersion('Preferences', self.prefs.mameExe, mameDisp)
                mameCfgMameVersion = getMameExeVersion('Mame.cfg', self.mameCfg.executable, mameDisp)

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
            if self.prefs.amDir != self.configUi.amDir.text() or self.prefs.mameExe != self.configUi.mameExe.text():
                self.loadPrefs()
                self.prefs.amDir = self.configUi.amDir.text()
                self.prefs.mameExe = self.configUi.mameExe.text()
                self.prefs.saveJSON(self.prefsFile)
        else:
            self.configUi.amDir.setText(currAmDir)
            self.configUi.mameExe.setText(currMameExe)
        return rsp

    def showPreferencesNoRsp(self):
        self.showPreferences()

    def dataChanged(self):
        if len(self.dispDict) > 0:
            for d in self.dispDict.keys():
                if d != 'Favorites' and self.dispDict[d].dataChanged:
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

    def setDisplayGroupMode(self, displayName, groupMode, groupBtn):
        if self.dispDict[displayName].groupMode == groupMode:
            if not groupBtn.isChecked():
                self.currentDisplay = displayName
                groupBtn.setChecked(True)

    def loadDisplay(self, displayName):
        # action = self.sender()
        if displayName != self.currentDisplay:
            self.searchOn = False
            self.currentDisplay = displayName
            displayLoaded = False
            self.titleBtn.setDisabled(False)
            self.parentBtn.setDisabled(False)
            if displayName == 'Favorites':
                self.treeWidget.hideColumn(self.col_idx['Favorite'])
                if not self.noneBtn.isChecked():
                    self.noneBtn.setChecked(True)
                    displayLoaded = True
                else:
                    self.dispDict[displayName].groupMode = 'none'
                self.titleBtn.setDisabled(True)
                self.parentBtn.setDisabled(True)
            else:
                self.treeWidget.showColumn(self.col_idx['Favorite'])
                if not self.dispDict[displayName].clonesExist:
                    self.parentBtn.setDisabled(True)
                    if self.dispDict[displayName].groupMode == 'parent':
                        self.dispDict[displayName].groupMode = 'title'

                if self.dispDict[displayName].groupMode == 'parent':
                    if not self.parentBtn.isChecked():
                        self.parentBtn.setChecked(True)
                        displayLoaded = True
                elif self.dispDict[displayName].groupMode == 'title':
                    if not self.titleBtn.isChecked():
                        self.titleBtn.setChecked(True)
                        displayLoaded = True
                else:
                    if not self.noneBtn.isChecked():
                        self.noneBtn.setChecked(True)
                        displayLoaded = True

            if not displayLoaded:
                self.loadTree(displayName, self.dispDict[displayName].groupMode)

            self.treeWidget.sortByColumn(self.col_idx['Title'], Qt.AscendingOrder)
            self.setMenuIcons()
            self.updateWinTitle()

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
        self.noneBtn.setText(_translate("MainWindow", "None"))
        self.uncheckedBtn.setText(_translate("MainWindow", "Hide Unchecked"))
        self.findDupButton.setText(_translate("MainWindow", "Find Duplicates"))

    def updateFileMenu(self):
        if self.dataChanged():
            self.saveAct.setEnabled(True)
        if 'Favorites' in self.dispDict.keys():
            if self.dispDict['Favorites'].dataChanged:
                self.favoritesAct.setEnabled(True)
            else:
                self.favoritesAct.setEnabled(False)
        else:
            self.favoritesAct.setText('Merge Favorites')
            self.favoritesAct.setEnabled(True)

    def updateWinTitle(self):
        title = 'AttractMode List Manager'
        if self.dataChanged():
            title = '* '+title
        if self.dispDict[self.currentDisplay].dataChanged:
            title += ' - * '+self.currentDisplay
        else:
            title += ' - '+self.currentDisplay

        self.setWindowTitle(QtCore.QCoreApplication.translate("MainWindow", title))

    def treeItemChanged(self, item, column):
        if not self.treeLoading:
            self.dispDict[self.currentDisplay].dataChanged = True
            self.updateWinTitle()
            self.updateFileMenu()
            # self.setWindowTitle(QtCore.QCoreApplication.translate("MainWindow", self.windowTitle+' *'))
            if item.parent() or self.dispDict[self.currentDisplay].groupMode == 'none':
                newLine = self.getTreeItemLineDictVal(item, 'LstLine')

                if column == self.col_idx['Title']:
                    if item.checkState(self.col_idx['Title']) == QtCore.Qt.Checked:
                        newLine = self.removeLineFieldVal(newLine, 'Extra', 'excluded')
                        self.setTreeItemLineDictVal(item, 'Excluded', 'N')
                    else:
                        newLine = self.addLineFieldVal(newLine, 'Extra', 'excluded')
                        self.setTreeItemLineDictVal(item, 'Excluded', 'Y')

                self.setTreeItemLineDictVal(item, 'LstLine', newLine)

    def toggleParentMode(self):
        radioButton = self.sender()
        if radioButton.isChecked():
            if radioButton.objectName() == 'parentBtn':
                self.dispDict[self.currentDisplay].groupMode = 'parent'
                self.expColBtn.setDisabled(False)
                self.cloneBtn.setDisabled(False)
                self.uncheckedBtn.setDisabled(False)
            elif radioButton.objectName() == 'titleBtn':
                self.dispDict[self.currentDisplay].groupMode = 'title'
                self.expColBtn.setDisabled(False)
                self.cloneBtn.setDisabled(True)
                self.uncheckedBtn.setDisabled(False)
            elif radioButton.objectName() == 'noneBtn':
                self.dispDict[self.currentDisplay].groupMode = 'none'
                self.expColBtn.setDisabled(True)
                self.cloneBtn.setDisabled(True)
                if self.currentDisplay == 'Favorites':
                    # if self.uncheckedBtn.text() == 'Show Unchecked':
                    #     self.toggleUncheckedHidden()
                    self.uncheckedBtn.setDisabled(True)
                else:
                    self.uncheckedBtn.setDisabled(False)
            self.loadTree(self.currentDisplay, self.dispDict[self.currentDisplay].groupMode)
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
        if field in self.listHeaderIdx.keys():
            return line.split(';')[self.listHeaderIdx[field]]
        else:
            return None

    def getRomLineDictVal(self, rom_name, field):
        if rom_name != '':
            if rom_name in self.dispDict[self.currentDisplay].romDict:
                lineDict = self.dispDict[self.currentDisplay].romDict[rom_name].lineDict
                if field in lineDict:
                    return self.dispDict[self.currentDisplay].romDict[rom_name].lineDict[field]
        return ''

    def getTreeItemLineDictVal(self, tree_item, field):
        rom_name = tree_item.text(self.col_idx['Name'])
        return self.getRomLineDictVal(rom_name, field)

    def setRomLineDictVal(self, rom_name, field, value):
        if rom_name != '':
            if rom_name in self.dispDict[self.currentDisplay].romDict:
                lineDict = self.dispDict[self.currentDisplay].romDict[rom_name].lineDict
                if field in lineDict:
                    self.dispDict[self.currentDisplay].romDict[rom_name].lineDict[field] = value
        return ''

    def setTreeItemLineDictVal(self, tree_item, field, value):
        rom_name = tree_item.text(self.col_idx['Name'])
        self.setRomLineDictVal(rom_name, field, value)

    def getSelectedColValueCount(self, column_name, col_value):
        item_count = 0
        value_count = 0
        selected_items = self.treeWidget.selectedItems()
        for tree_item in selected_items:
            if tree_item.parent() or self.dispDict[self.currentDisplay].groupMode == 'none':
                if self.currentDisplay == 'Favorites':
                    emu = self.getTreeItemLineDictVal(tree_item, 'Emulator')
                    rom_name = self.getTreeItemLineDictVal(tree_item, 'Name')
                    if emu in self.dispDict.keys():
                        emuDisp = self.dispDict[emu]
                        if rom_name in emuDisp.romDict.keys():
                            if column_name == 'favorite' and emuDisp.romDict[rom_name].lineDict['Locked'] == 'N':
                                item_count += 1
                                # if self.getTreeItemLineDictVal(tree_item, 'Favorite') == col_value:
                                #     value_count += 1
                elif column_name == 'locked' or self.getTreeItemLineDictVal(tree_item, 'Locked') == 'N':
                    item_count += 1
                    if self.currentDisplay != 'Favorites':
                        if (
                                (column_name == 'checked'
                                 and (tree_item.checkState(self.col_idx['Title']) == QtCore.Qt.Checked) == col_value)
                                or
                                (column_name == 'locked'
                                 and self.getTreeItemLineDictVal(tree_item, 'Locked') == col_value)
                                or
                                (column_name == 'favorite'
                                 and self.getTreeItemLineDictVal(tree_item, 'Favorite') == col_value)
                                or
                                (column_name == 'status'
                                 and self.getTreeItemLineDictVal(tree_item, 'Status') == col_value)
                        ):
                            value_count += 1
        return item_count, value_count

    def setItemLocked(self, tree_item, isLocked):
        if tree_item.parent() or self.dispDict[self.currentDisplay].groupMode == 'none':
            lockedFlag = 'N'
            if isLocked:
                tree_item.setIcon(self.col_idx['Variation'], self.lockIcon)
                lockedFlag = 'Y'
            else:
                tree_item.setIcon(self.col_idx['Variation'], self.unlockIcon)

            self.setTreeItemLineDictVal(tree_item, 'Locked', lockedFlag)
            self.setLockIcon(tree_item)

    def setSelectedLockStatus(self, status):
        selected_items = self.treeWidget.selectedItems()
        for tree_item in selected_items:
            if tree_item.parent() or self.dispDict[self.currentDisplay].groupMode == 'none':
                if status == 'toggle':
                    self.setItemLocked(tree_item, self.self.dispDict[self.currentDisplay](tree_item, 'Locked') == 'N')
                else:
                    self.setItemLocked(tree_item, status == 'lock')

    def setLockedContextMenu(self, menu, point):
        name = ""
        item_count, locked_count = self.getSelectedColValueCount('locked', 'Y')

        if item_count > 0:
            if item_count == 1:
                name = " "+self.treeWidget.itemAt(point).text(self.col_idx['Title'])

            if locked_count > 0 and locked_count != item_count:
                action = menu.addAction("Toggle locked")
                action.triggered.connect(functools.partial(self.setSelectedLockStatus, 'toggle'))

            if locked_count > 0:
                action = menu.addAction("Unlock"+name)
                action.triggered.connect(functools.partial(self.setSelectedLockStatus, 'unlock'))

            if locked_count < item_count:
                action = menu.addAction("Lock"+name)
                action.triggered.connect(functools.partial(self.setSelectedLockStatus, 'lock'))

    def setItemFavorite(self, tree_item, isFavorite):
        display = self.dispDict[self.currentDisplay]
        rom_name = tree_item.text(self.col_idx['Name'])
        if display.romDict[rom_name].lineDict['Locked'] == 'N' and rom_name != '':
            if tree_item.parent() or display.groupMode == 'none':
                if isFavorite:
                    favoriteFlag = 'Y'
                    if rom_name not in display.favList:
                        display.favList.append(rom_name)
                else:
                    favoriteFlag = 'N'
                    if rom_name in display.favList:
                        display.favList.remove(rom_name)

                display.romDict[rom_name].lineDict['Favorite'] = favoriteFlag
                self.setFavoriteIcon(tree_item)
                if self.currentDisplay == 'Favorites':
                    emu = self.getTreeItemLineDictVal(tree_item, 'Emulator')
                    if emu in self.dispDict.keys():
                        emuDisp = self.dispDict[emu]
                        if rom_name in emuDisp.romDict.keys():
                            emuDisp.romDict[rom_name].lineDict['Favorite'] = favoriteFlag
                            emuDisp.dataChanged = True
                            if favoriteFlag == 'N':
                                display.dataChanged = True
                                display.romDict.pop(rom_name)
                                results = self.treeWidget.findItems(rom_name,
                                                                    QtCore.Qt.MatchExactly,
                                                                    self.column_headers.index('Name'))
                                root = self.treeWidget.invisibleRootItem()
                                for item in results:
                                    root.removeChild(item)
                                if len(results) > 0:
                                    self.dispDict['Favorites'].dataChanged = True
                                    self.updateWinTitle()
                                    self.updateFileMenu()
                else:
                    if 'Favorites' in self.dispDict.keys():
                        favDisp = self.dispDict['Favorites']
                        if favoriteFlag == 'N':
                            if rom_name in favDisp.romDict.keys():
                                favDisp.romDict.pop(rom_name)
                                favDisp.dataChanged = True
                                self.updateWinTitle()
                                self.updateFileMenu()
                        else:
                            if rom_name not in favDisp.romDict.keys():
                                favDisp.romDict[rom_name] = recordtype('romItem', [('lineDict', {})])
                                favDisp.romDict[rom_name].lineDict = dict(display.romDict[rom_name].lineDict)
                                favDisp.dataChanged = True
                                self.updateWinTitle()
                                self.updateFileMenu()

    def setSelectedFavoriteStatus(self, status):
        selected_items = self.treeWidget.selectedItems()
        for tree_item in selected_items:
            if tree_item.parent() or self.dispDict[self.currentDisplay].groupMode == 'none':
                if status == 'toggle':
                    self.setItemFavorite(tree_item, self.getTreeItemLineDictVal(tree_item, 'Favorite') == 'N')
                else:
                    self.setItemFavorite(tree_item, status == 'Y')

    def setFavoriteContextMenu(self, menu, point):
        name = ""
        item_count, favorite_count = self.getSelectedColValueCount('favorite', 'N')

        if item_count > 0:
            if item_count == 1:
                name = " "+self.treeWidget.itemAt(point).text(self.col_idx['Title'])

            if favorite_count > 0 and favorite_count != item_count:
                action = menu.addAction("Toggle favorites")
                action.triggered.connect(functools.partial(self.setSelectedFavoriteStatus, 'toggle'))

            if favorite_count > 0:
                action = menu.addAction("Add"+name+" to favorites")
                action.triggered.connect(functools.partial(self.setSelectedFavoriteStatus, 'Y'))

            if favorite_count < item_count:
                action = menu.addAction("Remove "+name+" from favorites")
                action.triggered.connect(functools.partial(self.setSelectedFavoriteStatus, 'N'))

    def validateSelected(self, status):
        if os.path.isdir(self.prefs.amDir):
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
            if tree_item.parent() or self.dispDict[self.currentDisplay].groupMode == 'none':
                romStatus = self.dispDict[self.currentDisplay].\
                    romDict[tree_item.text(self.col_idx['Name'])].lineDict['Status']
                if status == 'selected' or status == romStatus:
                    rom_name = tree_item.text(self.col_idx['Name'])
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
                name = " "+self.treeWidget.itemAt(point).text(self.col_idx['Title'])

            if fail_count == 0 or fail_count == item_count:
                action = menu.addAction("Validate"+name)
                action.triggered.connect(functools.partial(self.validateSelected, 'selected'))
            else:
                if self.dispDict[self.currentDisplay].cfgDict['validateExe'] != 'Unknown':
                    action = menu.addAction("Validate failed")
                    action.triggered.connect(functools.partial(self.validateSelected, 'fail'))
                    action = menu.addAction("Validate passed")
                    action.triggered.connect(functools.partial(self.validateSelected, 'pass'))
                    action = menu.addAction("Validate selected")
                    action.triggered.connect(functools.partial(self.validateSelected, 'selected'))

    def setSelectedCheckStatus(self, status):
        selected_items = self.treeWidget.selectedItems()
        for tree_item in selected_items:
            if ((tree_item.parent() or self.dispDict[self.currentDisplay].groupMode == 'none')
                    and self.getTreeItemLineDictVal(tree_item, 'Locked') == 'N'):
                if status == 'check':
                    tree_item.setCheckState(self.col_idx['Title'], Qt.Checked)
                elif status == 'uncheck':
                    tree_item.setCheckState(self.col_idx['Title'], Qt.Unchecked)
                elif status == 'toggle':
                    if tree_item.checkState(self.col_idx['Title']) == QtCore.Qt.Checked:
                        tree_item.setCheckState(self.col_idx['Title'], Qt.Unchecked)
                    else:
                        tree_item.setCheckState(self.col_idx['Title'], Qt.Checked)

    def setCheckedContextMenu(self, menu, point):
        name = ""
        item_count, unchecked_count = self.getSelectedColValueCount('checked', False)

        if item_count > 0:
            if item_count == 1:
                name = " "+self.treeWidget.itemAt(point).text(self.col_idx['Title'])

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
            if (not self.hideUncheckedOn
                    or item.checkState(self.col_idx['Title']) == Qt.Checked
                    or self.currentDisplay == 'Favorites'):
                item.setHidden(False)
                if item.parent():
                    item.parent().setHidden(False)
                    if self.findUi.cbxInclSiblings.isChecked():
                        for cIdx in range(item.parent().childCount()):
                            if (not self.hideUncheckedOn
                                    or item.parent().child(cIdx).checkState(self.col_idx['Title']) == Qt.Checked):
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
        dirName = os.path.dirname(os.path.realpath(self.prefs.mameExe))
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
        for i, h in enumerate(self.listHeaderIdx):
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
            if listName not in ('', 'Favorites') and len(self.dispDict[listName].romDict) > 0:
                fileToOpen = os.path.join(self.prefs.amDir, "romlists\\"+listName+".tag")
                with open(fileToOpen, "w") as of:
                    for romItem in sorted(self.dispDict[listName].romDict.values(),
                                          key=lambda kv: kv.lineDict['Title']):
                        if romItem.lineDict['Favorite'] == 'Y':
                            wordList = romItem.lineDict['LstLine'].strip('\n\r').split(';')
                            rom_name = wordList[self.listHeaderIdx['Name']]
                            of.write(rom_name+'\n')
        except Exception as saveTagExcept:
            traceback.print_exc()
            raise saveTagExcept

    def saveAlm(self, listName):
        if listName not in ('', 'Favorites') and len(self.dispDict[listName].romDict) > 0:
            fileToOpen = os.path.join(self.prefs.amDir, "romLists\\"+listName+".alm")
            with open(fileToOpen, "w") as of:
                of.write('#Name;Excluded;Locked;Status\n')
                for romItem in sorted(self.dispDict[listName].romDict.values(), key=lambda kv: kv.lineDict['Title']):
                    if romItem.lineDict['LstLine'] == '':
                        continue
                    wordList = romItem.lineDict['LstLine'].strip('\n\r').split(';')
                    rom = wordList[self.listHeaderIdx['Name']]
                    romStatus = self.dispDict[listName].romDict[rom].lineDict['Status']
                    if self.dispDict[listName].romDict[rom].lineDict['Locked'] == 'Y' or\
                            self.dispDict[listName].romDict[rom].lineDict['Excluded'] == 'Y' or\
                            romStatus != '':
                        newLine = rom
                        if self.dispDict[listName].romDict[rom].lineDict['Excluded'] == 'Y':
                            newLine += ';Y'
                        else:
                            newLine += ';N'
                        if self.dispDict[listName].romDict[rom].lineDict['Locked'] == 'Y':
                            newLine += ';Y'
                        else:
                            newLine += ';N'
                        if romStatus != '':
                            newLine += ';'+romStatus
                        else:
                            newLine += ';unknown'
                        of.write(newLine+'\n')

    def updateFavorites(self):
        if self.favoritesAct.text() == 'Save':
            self.saveDisplay('Favorites')
        else:
            favAction = None
            if 'Favorites' in self.dispDict.keys():
                favAction = self.dispDict['Favorites'].action
                self.dispDict.pop('Favorites')
                self.dispDict['Favorites'] = newDisplayCfg('none')
            else:
                self.dispDict['Favorites'] = newDisplayCfg('none')
                self.addMenu('Display', self.dispDict, self.loadDisplay)

            if favAction is not None:
                self.dispDict['Favorites'].action = favAction

            for dispName, disp in self.dispDict.items():
                if dispName != 'Favorites':
                    for rom_name, rom_item in disp.romDict.items():
                        if rom_item.lineDict['Favorite'] == 'Y':
                            self.dispDict['Favorites'].romDict[rom_name] = self.romItem(lineDict=rom_item.lineDict)

            self.loadDisplay('Favorites')
            self.favoritesAct.setText('Save')
            self.favoritesAct.setIcon(self.saveIcon)
        self.updateFileMenu()

    def saveFavoritesTxt(self):
        favList = list()
        favDisp = None

        if 'Favorites' in self.dispDict.keys():
            favDisp = self.dispDict['Favorites']
            favDisp.romDict.clear()

        for dispName, disp in self.dispDict.items():
            if dispName != 'Favorites':
                for rom_name, rom_item in disp.romDict.items():
                    if rom_item.lineDict['Favorite'] == 'Y':
                        favList.append(rom_item)
                        favDisp.romDict[rom_name] = self.romItem(lineDict=rom_item.lineDict)

        self.loadTree('Favorites', 'none')

        if len(favList) > 0:
            fileToOpen = os.path.join(self.prefs.amDir, "romlists\\" + "Favorites.txt")
            with open(fileToOpen, "w") as of:
                of.write(self.fileHeader)
                for romItem in sorted(favList, key=lambda kv: kv.lineDict['Title']):
                    of.write(romItem.lineDict['LstLine']+'\n')

    def saveDisplay(self, dispName):
        if self.dispDict[dispName].dataChanged and len(self.dispDict[dispName].romDict) > 0:
            fileToOpen = os.path.join(self.prefs.amDir, "romlists\\" + dispName + ".txt")
            with open(fileToOpen, "w") as of:
                of.write(self.fileHeader)
                for romItem in sorted(self.dispDict[dispName].romDict.values(), key=lambda kv: kv.lineDict['Title']):
                    of.write(romItem.lineDict['LstLine'] + '\n')
            self.saveAlm(dispName)
            self.saveTag(dispName)
            self.dispDict[dispName].dataChanged = False
            print('Saved ' + dispName + ' to ' + fileToOpen)
            if dispName == 'Favorites':
                if self.dataChanged():
                    self.saveAct.setEnabled(False)
                self.updateWinTitle()
                self.updateFileMenu()

    def saveChangedDisplays(self):
        try:
            for d in self.dispDict.keys():
                if self.dispDict[d].dataChanged and len(self.dispDict[d].romDict) > 0:
                    self.saveDisplay(d)

            self.saveAct.setEnabled(False)
            self.updateWinTitle()
            self.updateFileMenu()

        except Exception as saveListExcept:
            traceback.print_exc()
            raise saveListExcept

    def setLockIcon(self, tree_item):
        if tree_item.parent() or self.dispDict[self.currentDisplay].groupMode == 'none':
            if self.currentDisplay == 'Favorites':
                emuDisp = self.getTreeItemLineDictVal(tree_item, 'Emulator')
                rom_name = self.getTreeItemLineDictVal(tree_item, 'Name')
                locked = self.dispDict[emuDisp].romDict[rom_name].lineDict['Locked']
            else:
                locked = self.getTreeItemLineDictVal(tree_item, 'Locked')
            if locked == 'Y':
                tree_item.setIcon(self.col_idx['Variation'], self.lockIcon)
            else:
                tree_item.setIcon(self.col_idx['Variation'], self.unlockIcon)

    def setFavoriteIcon(self, tree_item):
        if (self.getTreeItemLineDictVal(tree_item, 'Name') != '' or
                self.dispDict[self.currentDisplay].groupMode == 'none'):
            if self.currentDisplay == 'Favorites':
                tree_item.setIcon(self.col_idx['Favorite'], self.blankIcon)
            else:
                # if self.getTreeItemLineDictVal(tree_item, 'Favorite') == 'Y':
                if self.dispDict[self.currentDisplay].romDict[self.getTreeItemLineDictVal(tree_item, 'Name')].lineDict['Favorite'] == 'Y':
                    tree_item.setIcon(self.col_idx['Favorite'], self.starIcon)
                else:
                    tree_item.setIcon(self.col_idx['Favorite'], self.blankIcon)

    def setStatusIcon(self, tree_item):
        if tree_item.parent() or self.dispDict[self.currentDisplay].groupMode == 'none':
            if self.currentDisplay == 'Favorites':
                emuDisp = self.getTreeItemLineDictVal(tree_item, 'Emulator')
                rom_name = self.getTreeItemLineDictVal(tree_item, 'Name')
                status = self.dispDict[emuDisp].romDict[rom_name].lineDict['Status']
            else:
                status = self.getTreeItemLineDictVal(tree_item, 'Status')
            if status == 'pass':
                tree_item.setIcon(self.col_idx['Status'], self.passIcon)
            elif status == 'fail':
                tree_item.setIcon(self.col_idx['Status'], self.failIcon)
            else:
                tree_item.setIcon(self.col_idx['Status'], self.blankIcon)

    def setCheckedHiddenStatus(self, treeItem):
        if self.currentDisplay != 'Favorites':
            if self.getTreeItemLineDictVal(treeItem, 'Excluded') == 'Y':
                treeItem.setCheckState(self.col_idx['Title'], Qt.Unchecked)
                if self.hideUncheckedOn:
                    treeItem.setHidden(True)
            else:
                treeItem.setCheckState(self.col_idx['Title'], Qt.Checked)

    def setUpItem(self, treeItem, itemType, lineDict):
        treeItem.setText(self.col_idx['Title'], lineDict['NewTitle'])
        if self.dispDict[self.currentDisplay].groupMode == 'none' or itemType == 'child':
            for k in self.col_idx.keys():
                col = k.split('(')[0].strip()
                if col not in ['Title', 'Status', 'Favorite']:
                    if col in lineDict.keys():
                        treeItem.setText(self.col_idx[k], lineDict[col])

        self.setCheckedHiddenStatus(treeItem)
        if self.dispDict[self.currentDisplay].groupMode == 'none' or itemType == 'child':
            self.setFavoriteIcon(treeItem)
            self.setLockIcon(treeItem)
            self.setStatusIcon(treeItem)

    def addParent(self, mode, lineDict):
        gameIdx = self.treeWidget.topLevelItemCount()
        if mode == 'parent':
            self.parentCloneOfDict[lineDict['Name']] = gameIdx
        elif mode == 'title':
            if lineDict['NewTitle'] not in self.parentTitleDict:
                self.parentTitleDict[lineDict['NewTitle']] = gameIdx
        self.treeWidget.addTopLevelItem(QTreeWidgetItem(gameIdx))
        treeItem = self.treeWidget.topLevelItem(gameIdx)
        treeItem.setFlags(int(treeItem.flags()) | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsTristate)
        self.setUpItem(treeItem, 'parent', lineDict)
        return treeItem

    def addChild(self, treeItem, lineDict):
        childItem = QTreeWidgetItem()
        treeItem.insertChild(treeItem.childCount(), childItem)
        self.setUpItem(childItem, 'child', lineDict)

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
            if self.dispDict[self.currentDisplay].groupMode == 'none':
                self.MyMessage.setText(
                    "{} Games ({} hidden)".format(
                        titleCount - hiddenGroupCount,
                        hiddenGroupCount))
            else:
                self.MyMessage.setText(
                    "{} Groups ({} hidden) containing {} games ({} hidden)".format(
                        titleCount - hiddenGroupCount,
                        hiddenGroupCount,
                        len(self.dispDict[self.currentDisplay].romDict) - hiddenChildCount,
                        hiddenChildCount)
                )
        else:
            if self.dispDict[self.currentDisplay].groupMode == 'none':
                self.MyMessage.setText("{} Games".format(titleCount))
            else:
                self.MyMessage.setText(
                    "{} Groups containing {} games".format(titleCount,
                                                           len(self.dispDict[self.currentDisplay].romDict)))

    def loadTree(self, listName, mode):
        self.currentDisplay = listName

        if len(self.dispDict[self.currentDisplay].romDict) == 0:
            return

        self.treeWidget.clear()
        app.processEvents()

        self.treeWidget.setSortingEnabled(False)
        self.parentCloneOfDict.clear()
        self.parentTitleDict.clear()

        d = QtWidgets.QDialog()
        dui = ProgressDialog(parent=self, flags=Qt.Dialog)
        dui.setupUi(d)
        d.show()
        levelList = ['parent']
        if mode != 'none':
            levelList.append('child')

        dui.setProgressRange(1, len(self.dispDict[self.currentDisplay].romDict)*len(levelList))

        idx = 0
        self.treeLoading = True

        for level in levelList:
            for romname, romItem in self.dispDict[self.currentDisplay].romDict.items():
                line = romItem.lineDict['LstLine']
                if line.strip() == '':
                    continue
                try:
                    if dui.isCancelled():
                        break
                    # wordlist = line.strip('\n\r').split(';')
                    lineDict = romItem.lineDict
                    cloneOf = lineDict['CloneOf']
                    newTitle = lineDict['NewTitle']

                    if mode == 'none':
                        self.addParent(mode, lineDict)
                    if mode == 'parent':
                        if level == 'parent':
                            if cloneOf == "":
                                treeItem = self.addParent(mode, lineDict)
                                self.addChild(treeItem, lineDict)
                                for k in {'Variation', 'CloneOf', 'Favorite'}:
                                    treeItem.setText(self.col_idx[k], '')
                        else:
                            if cloneOf != "":
                                if cloneOf in self.parentCloneOfDict.keys():
                                    gameIdx = self.parentCloneOfDict[cloneOf]
                                    self.addChild(self.treeWidget.topLevelItem(gameIdx), lineDict)
                                else:
                                    # Parent ROM not found, create dummy parent using cloneOf value
                                    treeItem = self.addParent(mode, lineDict)
                                    self.addChild(treeItem, lineDict)
                                    treeItem.setText(self.col_idx['Name'], lineDict['CloneOf'])
                    elif mode == 'title':
                        if level == 'parent':
                            if newTitle not in self.parentTitleDict:
                                treeItem = self.addParent(mode, lineDict)
                                for k in {'Variation', 'CloneOf', 'Favorite'}:
                                    treeItem.setText(self.col_idx[k], '')
                        else:
                            gameIdx = self.parentTitleDict[newTitle]
                            treeItem = self.treeWidget.topLevelItem(gameIdx)
                            self.addChild(treeItem, lineDict)
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
        if mode == 'parent':
            self.treeWidget.sortByColumn(self.col_idx['CloneOf'], Qt.AscendingOrder)
        self.treeWidget.sortByColumn(self.col_idx['Title'], Qt.AscendingOrder)
        self.treeWidget.resizeColumnToContents(self.col_idx['Title'])
        self.treeWidget.setColumnWidth(self.col_idx['Favorite'], 65)
        self.treeWidget.setColumnWidth(self.col_idx['Rotation'], 65)
        self.treeWidget.setColumnWidth(self.col_idx['Buttons'], 65)
        self.treeWidget.setColumnWidth(self.col_idx['Players'], 65)
        self.treeWidget.setColumnWidth(self.col_idx['Status'], 50)
        self.treeWidget.expandAll()
        self.expColBtn.setText("Collapse")
        app.processEvents()
        print('Loaded tree from '+listName)

    def loadList(self, listName):
        try:
            # self.printDispCfg(listName)

            fileToOpen = os.path.join(self.prefs.amDir, "romlists\\" + listName + ".txt")
            if os.path.exists(fileToOpen):
                self.dispDict[listName].dataChanged = False
                self.treeWidget.clear()
                self.dispDict[listName].romDict.clear()
                self.parentCloneOfDict.clear()
                self.listHeaderIdx.clear()

                self.treeWidget.setSortingEnabled(False)
                with open(fileToOpen) as fp:
                    line = fp.readline()
                    if line:
                        self.fileHeader = line
                        headerlist = line.strip('# \n').split(';')
                        for i, header in enumerate(headerlist):
                            self.listHeaderIdx[header] = i
                    else:
                        print("No header for ", listName)
                        return

                    self.emuDict.clear()
                    line = fp.readline()
                    while line:
                        if line.strip() == '':
                            line = fp.readline()
                            continue

                        lineDict = {'Status': 'Unknown', 'Favorite': 'N', 'Locked': 'N', 'Excluded': 'N', 'LstLine': ''}
                        wordlist = line.strip('\n\r').split(';')
                        for k in self.col_idx.keys():
                            if k in self.listHeaderIdx.keys():
                                lineDict[k] = wordlist[self.listHeaderIdx[k]]

                        lineDict['LstLine'] = line.strip('\n')
                        self.dispDict[listName].romDict[lineDict['Name']] = self.romItem(lineDict=lineDict)
                        lineDict['NewTitle'], lineDict['Variation'] = getTitleVariation(lineDict['Title'])

                        if lineDict['Emulator'] not in self.emuDict.keys():
                            self.emuDict[lineDict['Emulator']] = 'None'
                        line = fp.readline()
#                    self.addMenu('Emulator', self.emuDict, self.loadDisplay)

                if self.firstLoad:
                    bkpFile = os.path.join(fileToOpen+".bkp")
                    with open(bkpFile, "w") as of:
                        of.write(self.fileHeader)
                        for romItem in self.dispDict[listName].romDict.values():
                            of.write(romItem.lineDict['LstLine']+'\n')

                if listName != 'Favorites':
                    fileToOpen = os.path.join(self.prefs.amDir, "romlists\\" + listName + ".tag")
                    if os.path.exists(fileToOpen):
                        with open(fileToOpen) as fp:
                            line = fp.readline()
                            while line:
                                fav_rom = line.strip('\n\r')
                                self.dispDict[listName].favList.append(fav_rom)
                                if fav_rom in self.dispDict[listName].romDict:
                                    self.dispDict[listName].romDict[fav_rom].lineDict['Favorite'] = 'Y'
                                line = fp.readline()

                if self.firstLoad:
                    bkpFile = os.path.join(fileToOpen+".bkp")
                    with open(bkpFile, "w") as of:
                        for fav_rom in self.dispDict[listName].favList:
                            of.write(fav_rom+'\n')

                if listName != 'Favorites':
                    fileToOpen = os.path.join(self.prefs.amDir, "romlists\\" + listName + ".alm")

                    if os.path.exists(fileToOpen):
                        with open(fileToOpen) as fp:
                            # Read in the header
                            # TODO actually use header
                            fp.readline().strip('\n')
                            # Read the first line
                            line = fp.readline().strip('\n')
                            while line:
                                almFields = line.split(';')
                                if almFields[0] in self.dispDict[listName].romDict:
                                    self.dispDict[listName].romDict[almFields[0]].lineDict['Excluded'] = almFields[1]
                                    self.dispDict[listName].romDict[almFields[0]].lineDict['Locked'] = almFields[2]
                                    self.dispDict[listName].romDict[almFields[0]].lineDict['Status'] = almFields[3]
                                else:
                                    self.dispDict[listName].romDict[almFields[0]] = self.romItem(excluded=almFields[1],
                                                                                                 locked=almFields[2])
                                line = fp.readline().strip('\n')

            print('Loaded list '+listName)
        except Exception as loadListExcept:
            traceback.print_exc()
            raise loadListExcept

    def validateRom(self, romname):
        if self.dispDict['Mame'].cfgDict['validateExe'] != 'Unknown':
            ret = subprocess.run(
                [self.prefs.mameExe, romname, "-verifyroms", "-rompath", self.mameCfg.rompath],
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
            rom_name = treeItem.text(self.col_idx['Name'])
            return_code = self.validateRom(rom_name)
            if return_code != 0:
                treeItem.setCheckState(self.col_idx['Title'], Qt.Unchecked)
                status = 'fail'
            else:
                status = 'pass'

            self.setTreeItemLineDictVal(treeItem, 'Status', status)
            self.setStatusIcon(treeItem)
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

            if self.dispDict[self.currentDisplay].groupMode == 'none':
                self.treeWidget.sortByColumn(self.col_idx['Title'], Qt.AscendingOrder)
                prevTitle = ''
                prevIdx   = -1
                for idx in range(titleCount):
                    item = root.child(idx)
                    if item.checkState(self.col_idx['Title']) == QtCore.Qt.Checked or self.currentDisplay == 'Favorites':
                        if item.text(self.col_idx['Title']) == prevTitle:
                            item.setHidden(False)
                            root.child(prevIdx).setHidden(False)
                        else:
                            item.setHidden(True)
                        prevTitle = item.text(self.col_idx['Title'])
                        prevIdx   = idx
            else:
                for idx in range(titleCount):
                    item = root.child(idx)
                    if (item.checkState(self.col_idx['Title']) == QtCore.Qt.Checked
                            or item.checkState(self.col_idx['Title']) == QtCore.Qt.PartiallyChecked):
                        romname = ""
                        variation = ""
                        checkedCount = 0
                        for cIdx in range(item.childCount()):
                            child = item.child(cIdx)
                            if child.checkState(self.col_idx['Title']) == QtCore.Qt.Checked:
                                checkedCount += 1
                                if checkedCount == 1:
                                    variation = child.text(self.col_idx['Variation'])
                                    romname = child.text(self.col_idx['Name'])

                        if checkedCount > 1:
                            item.setHidden(False)
                        else:
                            item.setText(self.col_idx['Variation'], variation)
                            item.setText(self.col_idx['Name'], romname)

                        for cIdx in range(item.childCount()):
                            child = item.child(cIdx)
                            if child.checkState(self.col_idx['Title']) == QtCore.Qt.Checked:
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
                if item.checkState(self.col_idx['Title']) != QtCore.Qt.Unchecked:
                    parentRom = ""
                    for cIdx in range(item.childCount()):
                        child = item.child(cIdx)
                        if child.checkState(self.col_idx['Title']) == QtCore.Qt.Checked:
                            if child.text(self.col_idx['CloneOf']) == "":
                                if parentRom == "":
                                    parentRom = child.text(self.col_idx['Name'])
                                elif parentRom != child.text(self.col_idx['Name']):
                                    parentRom = ""
                                    break
                    if parentRom != "":
                        for cIdx in range(item.childCount()):
                            child = item.child(cIdx)
                            if (child.checkState(self.col_idx['Title']) == QtCore.Qt.Checked
                                    and child.text(self.col_idx['CloneOf']) == parentRom
                                    and self.dispDict[self.currentDisplay].
                                    romDict[child.text(self.col_idx['Name'])].lineDict['Locked'] == 'N'):
                                child.setCheckState(self.col_idx['Title'], Qt.Unchecked)
#            self.findDuplicates()
        except Exception as unselectClonesExcept:
            traceback.print_exc()
            raise unselectClonesExcept

    def setUncheckedHidden(self, hidden):
        try:
            self.hideUncheckedOn = hidden
            if (self.searchOn and not hidden) or self.currentDisplay == 'Favorites':
                self.showSearchResults()
            else:
                root = self.treeWidget.invisibleRootItem()
                titleCount = root.childCount()
                for idx in range(titleCount):
                    item = root.child(idx)
                    checked_cnt = 0
                    unchecked_cnt = 0
                    other_cnt = 0
                    if self.dispDict[self.currentDisplay].groupMode == 'none':
                        if item.checkState(self.col_idx['Title']) == QtCore.Qt.Checked:
                            checked_cnt += 1
                        else:
                            unchecked_cnt += 1

                    for cIdx in range(item.childCount()):
                        child = item.child(cIdx)
                        if child.checkState(self.col_idx['Title']) == QtCore.Qt.Unchecked:
                            if hidden:
                                child.setHidden(True)
                            else:
                                if not self.searchOn:
                                    child.setHidden(False)
                            unchecked_cnt += 1
                        elif item.checkState(self.col_idx['Title']) != QtCore.Qt.Unchecked:
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
                if disp != 'Favorites':
                    self.loadList(disp)
                    self.dispDict[disp].clonesExist = False

                    for item in self.dispDict[disp].romDict.values():
                        if item.lineDict['CloneOf'] != '':
                            self.dispDict[disp].clonesExist = True
                            print('Found clones in '+disp)
                            break

            self.firstLoad = False
            self.loadTree(list(self.dispDict.keys())[0], 'parent')
            self.addMenu('Display', self.dispDict, self.loadDisplay)
            self.setMenuIcons()
            self.updateWinTitle()
            self.updateFileMenu()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    MainWindow = Ui_MainWindow()
    MainWindow.setupUi()
    MainWindow.show()
    MainWindow.loadPrefs()
    MainWindow.loadAllDisplays()

    try:
        sys.exit(app.exec_())
    except Exception as e:
        traceback.print_exc()
        raise e
