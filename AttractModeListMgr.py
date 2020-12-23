# importing libraries
import sys 
import subprocess
import os.path

from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import *
  
class amListMgr(QWidget): 
    infilepath = 'e:\\AttractMode\\romlists\\Mame.txt'
    outfilepath = 'e:\\AttractMode\\romlists\\MameValid.txt'

    def __init__(self): 
        super().__init__() 
  
        # calling initUI method 
        self.initUI() 
  
    # method for creating widgets 
    def initUI(self): 
  
        self.pbar = QProgressBar(self) 
        self.pbar.setGeometry(30, 40, 200, 25) 

        self.amDirLbl = QLabel(self)
        self.amDirLbl.setGeometry(10, 80, 65, 25)
        self.amDirLbl.setText("Directory")
        
        self.amDir = QLineEdit(self)
        self.amDir.setGeometry(80, 80, 200, 25)

        self.amDirBtn = QPushButton('...', self)
        self.amDirBtn.setGeometry(285, 80, 30, 25)
        self.amDirBtn.clicked.connect(self.openAmDirDialog)

        self.ptxt = QLabel(self)
        self.ptxt.setGeometry(30, 40, 200, 25)
        self.ptxt.setAlignment(Qt.AlignCenter)
        
        self.btn = QPushButton('Start', self) 
        self.btn.move(40, 120) 
        self.btn.clicked.connect(self.processList) 
  
        # setting window geometry 
        self.setGeometry(300, 300, 600, 340) 
  
        # setting window action 
        self.setWindowTitle("Python") 
  
        # showing all the widgets 

        self.show()


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
        print(lineCnt)
        return lineCnt

    def openAmDirDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if fileName:
            self.amDir.setText(os.path.normpath(fileName))

    # when button is pressed this method is being called 
    def processList(self): 
        idx = 0
        validCnt = 0
        cnt = self.getLineCount()

        if cnt > 1:
            of = open(self.outfilepath, "w")
            with open(self.infilepath) as fp:
                line = fp.readline()
                while line:
                    if idx > 0:
                        wordlist = line.split(';')
                        romname = "{0}".format(wordlist[0].strip())
                        try:
                            ret = subprocess.run(["e:\\mame\\mame64", romname, "-verifyroms", "-rompath", "e:\\mame\\roms"], stdout=subprocess.PIPE, text=True, shell=True)
                            validCnt += 1
                            if ret.returncode == 0:
                                of.write(line)
                                validCnt += 1
                        except:
                            print("Oops!", sys.exc_info()[0], "occurred.")
                    
                    idx += 1
                    self.ptxt.setText("{0} / {1}".format(idx, cnt))
                    try:
                        App.processEvents()
                    except:
                        print("Oops!", sys.exc_info()[0], "occurred.")
                       
                    self.pbar.setValue(int(idx/cnt*100))                  
                    line = fp.readline()
                    if idx >= 10:
                        self.pbar.setValue(100)
                        break
            of.close()
            fp.close()
                
# main method 
if __name__ == '__main__': 
      
      
    # create pyqt5 app 
    App = QApplication(sys.argv) 
  
    # create the instance of our Window 
    window = amListMgr() 
  
    # start the app 
    sys.exit(App.exec()) 
