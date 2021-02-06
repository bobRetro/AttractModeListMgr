from distutils.core import setup
import py2exe

setup(windows=[{"script":"AttractModeListMgr.py"}],
    options={"py2exe":{"includes":["PyQt5.sip", "PyQt5", "PyQt5.QtCore", "PyQt5.QtGui"]}},
    data_files = [("platforms", ["C:\\Users\\Video\\AppData\\Local\\Programs\\Python\\Python39\\Lib\\site-packages\\PyQt5\\Qt\\plugins\\platforms\\qwindows.dll"]),
                  ("imageformats",["C:\\Users\\Video\\AppData\\Local\\Programs\\Python\\Python39\\Lib\\site-packages\\PyQt5\\Qt\\plugins\\imageformats\\qicns.dll",
                                   "C:\\Users\\Video\\AppData\\Local\\Programs\\Python\\Python39\\Lib\\site-packages\\PyQt5\\Qt\\plugins\\imageformats\\qgif.dll",
                                   "C:\\Users\\Video\\AppData\\Local\\Programs\\Python\\Python39\\Lib\\site-packages\\PyQt5\\Qt\\plugins\\imageformats\\qico.dll",
                                   "C:\\Users\\Video\\AppData\\Local\\Programs\\Python\\Python39\\Lib\\site-packages\\PyQt5\\Qt\\plugins\\imageformats\\qjpeg.dll",
                                   "C:\\Users\\Video\\AppData\\Local\\Programs\\Python\\Python39\\Lib\\site-packages\\PyQt5\\Qt\\plugins\\imageformats\\qsvg.dll",
                                   "C:\\Users\\Video\\AppData\\Local\\Programs\\Python\\Python39\\Lib\\site-packages\\PyQt5\\Qt\\plugins\\imageformats\\qtga.dll",
                                   "C:\\Users\\Video\\AppData\\Local\\Programs\\Python\\Python39\\Lib\\site-packages\\PyQt5\\Qt\\plugins\\imageformats\\qtiff.dll",
                                   "C:\\Users\\Video\\AppData\\Local\\Programs\\Python\\Python39\\Lib\\site-packages\\PyQt5\\Qt\\plugins\\imageformats\\qwbmp.dll",
                                   "C:\\Users\\Video\\AppData\\Local\\Programs\\Python\\Python39\\Lib\\site-packages\\PyQt5\\Qt\\plugins\\imageformats\\qwebp.dll"]),
                  ("icons", ["icons\\error.ico", "icons\\Iconsmind-Outline-Yes.ico", "icons\\Lock.ico", "icons\\Star.ico", "icons\\Unlock.ico"]),
                  ("documentation",  ["documentation\\AttractMode List Manager.docx"]),
                  (".", ["LICENSE", "README.md"])
                 ]
    )
