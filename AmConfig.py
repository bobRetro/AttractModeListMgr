import json

class AmConfig:
    def __init__(self):    
        self.amDir = 'AttractMode'
        # self.outFilePath = 'MameValidated.txt'
        self.mameExe = 'mame64.exe'
        # self.display = list()
        # self.display.append("Mame")
        # self.display.append("Atari")
        
    def saveJSON(self, cfgFileName):
        print('Saving prefs '+cfgFileName)
        with open(cfgFileName, "w") as data_file:
            jsonString = json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
            linelist = jsonString.split('\n')
            for line in linelist:
                data_file.write(line+"\n")
    
    def loadJSON(self, cfgFileName):
        with open(cfgFileName, "r") as data_file:
            jsonData = json.load(data_file)
            if "amDir" in jsonData:
                self.amDir = jsonData["amDir"]
            # self.outFilePath = jsonData["outFilePath"]
            self.mameExe = jsonData["mameExe"]
            # self.display = jsonData["display"]
            # print(self.display)
            # print(self.display[1])
                    
