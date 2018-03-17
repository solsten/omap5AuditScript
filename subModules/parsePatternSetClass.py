'''
Created on Jan 12, 2018

@author: andersco
'''

from time import sleep     
from _collections import defaultdict

class parsePatternSetClass(object):
    def setPatternSetFilename(self, fileName):
        self.__patSetFileName = fileName

    
    def getPatternSets(self):
        if not self.__dataPulled:
            self.__pullData()
        return self.__patternSetInstances

   
    def getPatternSetPatterns(self):
        if not self.__dataPulled:
            self.__pullData()
        return self.__patternSetPatterns

   
    def getPatternSetNames(self):
        if not self.__dataPulled:
            self.__pullData()
        return self.__patternSetNames

   
    def doNothing(self):
        sleep(0)
        

    '''Private Functions''' 
    def __init__(self):
        self.__patSetFileName = "patternSetsAnalog.txt"
        self.__dataPulled = False
        self.__patternSetInstances = []
        self.__patternSetNames = set()
        self.__patternSetPatterns = defaultdict(list)
        
    
    def __pullData(self):
        if not self.__dataPulled:
            #find all the lines in the datalog that contain text "TestName:"
            with open(self.__patSetFileName,"r") as patSetFile:
                for (lineNum,line) in enumerate(patSetFile):
                    if lineNum > 2:
                        words = line.split()
                        patSet = words[0].strip()
                        patName = words[1].strip()
                        patName = patName.upper()
                        try:
                            patPath = patName.split("\\")
                            patName = patPath[2]
                            patName = patName[:-4]
                        except:
                            patName = patName
                        burstPat = words[2].strip()
                        self.__patternSetNames.add(patSet)
                        self.__patternSetPatterns[patSet].append(patName)
                        self.__patternSetInstances.append((patSet,patName,burstPat))                                                    
            self.__dataPulled = True
            patSetFile.close


#used to test class using runs as 
if __name__ == '__main__':
    patSet = parsePatternSetClass()
    
    patSets = patSet.getPatternSets()
    patSetNames = patSet.getPatternSetNames()
    patSetPats = patSet.getPatternSetPatterns()
    patSet.doNothing()