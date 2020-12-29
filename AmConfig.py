import json

class AmConfig:
    def __init__(self):    
        self.amDir = 'e:\\AttractMode'
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
            test = json.load(data_file)
            self.amDir = test["amDir"]
            self.outFilePath = test["outFilePath"]
            self.mameExe = test["mameExe"]

