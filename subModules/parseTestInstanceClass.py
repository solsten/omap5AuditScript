'''
Created on Jan 12, 2018

@author: andersco
'''

from time import sleep     
from _collections import defaultdict

class parseTestInstanceClass(object):
    def setTestInstFilename(self, fileName):
        self.__instFile = fileName

    
    def getPatternSets(self):
        if not self.__dataPulled:
            self.__pullData()
        return self.__patSets

   
    def doNothing(self):
        sleep(0)
        

    '''Private Functions''' 
    def __init__(self):
        self.__instFile = "Inst_Analog_FT1.txt"
        self.__dataPulled = False
        self.__testGroupArgList = ""
        self.__freqTests = []
        self.__viTests = []
        self.__patSets = defaultdict(list)
        
    
    def __pullData(self):
        if not self.__dataPulled:
            with open(self.__instFile,"r") as instFile:
                for line in instFile:
                    if "TestGroup" in line:
                        self.__getTestGroup(line)
            self.__dataPulled = True
            instFile.close()
            
    
    def __getTestGroup(self,line): 
        words = line.split()
        for word in words:
            upperCaseWord = word.upper()
            if (upperCaseWord[:3] == "TG_") and (upperCaseWord[-3:] == "_ST"):
                patternSet = word
        testName = words[0].upper()
        self.__viTests.append((testName,patternSet))
        self.__patSets[testName].append(patternSet)
            
    
            
    
#used to test class using runs as 
if __name__ == '__main__':
    testInst = parseTestInstanceClass()
    
    patSets = testInst.getPatSets()
    testInst.doNothing()