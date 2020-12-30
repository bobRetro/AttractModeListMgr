import json

class AmConfig:
    def __init__(self):    
        self.amDir = 'AttractMode'
        self.outFilePath = 'MameValidated.txt'
        self.mameExe = 'mame64.exe'
        
    def saveJSON(self, cfgFileName):
        with open(cfgFileName, "w") as data_file:
            jsonString = json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
            linelist = jsonString.split('\n')
            for line in linelist:
                data_file.write(line+"\n")
    
    def loadJSON(self, cfgFileName):
        with open(cfgFileName, "r") as data_file:
            jsonData = json.load(data_file)
            self.amDir = jsonData["amDir"]
            self.outFilePath = jsonData["outFilePath"]
            self.mameExe = jsonData["mameExe"]
                    
