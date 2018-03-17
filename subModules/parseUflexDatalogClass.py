'''
Created on Jan 3, 2018

@author: andersco
'''
from time import sleep    

LINE_NUM = 0
TEST_NAME = 1
PATTERN_NAME = 2
MEAS_NAME = 3
MIN_LIMIT = 4
MAX_LIMIT = 6
NOT_FOUND = 99

class parseUflexDatalogClass(object):
 
#public functions 
    def setDatalogFilename(self, datalogFileName):
        self.__datalogFileName = datalogFileName
 
        
    def getTestNames(self):
        if not self.__dataPulled:
            self.__pullData()
        return self.__testNames


    def getAnalogMeasNames(self):
        if not self.__dataPulled:
            self.__pullData()
        return self.__analogMeasNames


    def getPatternNames(self):           
        if not self.__dataPulled:
            self.__pullData()
        return self.__patternNames
    
    
    def getTestInstances(self):           
        if not self.__dataPulled:
            self.__pullData()
        return self.__testInstances
    
    
    def doNothing(self):
        sleep(0)
        

    '''Private Functions'''
    def __init__(self):
        self.__datalogFileName = "uflexDatalog.txt"
        self.__dataPulled = False
        self.__patternNames = set()
        self.__testNames = set()
        self.__analogMeasNames = set()
        self.__testInstances = []
        self.__testInstancesFound = set()     
        self.__analogTestInstancesFound = set()     
        self.__testLineNums = set()
        

    
    def __pullData(self):  
        if not self.__dataPulled:
            self.__getTestNames()
            self.__getDigitalAnalogTests()
            self.__dataPulled = True
  
    
    def __getTestNames(self):
        with open(self.__datalogFileName,"r") as datalogFile:
            for (lineNum,line) in enumerate(datalogFile):
                words = line.split()
                if len(words) == 1:
                    testName = words[0].strip()
                    if (testName[:1]=="<") and (testName[-1:]==">"):
                        testName = testName.upper() 
                        testInst = (testName,"","","","","","")                       
                        if testInst not in self.__testInstancesFound:
                            self.__testInstancesFound.add(testInst)
                            self.__testNames.add(testName)
                            self.__testLineNums.add(lineNum)
                            testInst = tuple([lineNum]) + testInst
                            self.__testInstances.append(testInst)
        datalogFile.close()
        self.__testLineNums = sorted(self.__testLineNums) #put them in order to make future searches easier 
        
    
    def __getDigitalAnalogTests(self):
        with open(self.__datalogFileName,"r") as datalogFile:
            for (lineNum,line) in enumerate(datalogFile):
                if "IMze_ckwglgn2FF_bp" in line:
                    self.doNothing()
                if lineNum in self.__testLineNums:
                    testName = self.__getTestName(lineNum)
                elif self.__isEfuseTest(line):
                    testInst = self.__getEfuseTestInst(line, testName)
                    if not self.__isDuplicateAnalogInst(testInst):
                        testInst = tuple([lineNum]) + testInst
                        self.__testInstances.append(testInst)
                        self.__analogMeasNames.add(testInst[MEAS_NAME])
                elif self.__isAnalogTest(line):
                    testInst = self.__getAnalogTestInst(line, testName)
                    if not self.__isDuplicateAnalogInst(testInst):
                        testInst = tuple([lineNum]) + testInst
                        self.__testInstances.append(testInst)
                        self.__analogMeasNames.add(testInst[MEAS_NAME])
                        measName = testInst[MEAS_NAME]
                elif self._isPatternTest(line): 
                    testInst = self.__getPatternTestInstance(line,measName)
                    if testInst not in self.__testInstancesFound:
                        self.__testInstancesFound.add(testInst)
                        testInst = tuple([lineNum]) + testInst
                        self.__testInstances.append(testInst)
                        temp = testInst[PATTERN_NAME]
                        self.__patternNames.add(testInst[PATTERN_NAME]) 
                        if "IMZE_CKWGLGN2FF_BP" in self.__patternNames:
                            self.doNothing()
                        self.__testNames.add(testInst[TEST_NAME])
        datalogFile.close()
    
    
    def __isEfuseTest(self, line):
        if "FF_CROM_MG0" in line:
            return False
        elif "OFF" in line:
            return False
        words = line.split()
        if len(words) > 2:
            if ("FF_" in words[2]) and ("2FF" not in words[2]):
                return True
            else:
                return False        
        else:
            return False        
    
    
    def __isDuplicateAnalogInst(self,findInst):
        #offset since the flow number not in int name
        testInst = (findInst[TEST_NAME-1],findInst[MEAS_NAME-1],findInst[MIN_LIMIT-1],findInst[MAX_LIMIT-1])
        if testInst in self.__analogTestInstancesFound:
            return True
        else:
            self.__analogTestInstancesFound.add(testInst)
            return False
    
    
    def __getEfuseTestInst(self,line,testName):
        if self.__isPassFailEfuse(line):
            words = line.split()
            testInst = (testName,"",words[2],"",words[3],"","")
        else:
            testInst = self.__getAnalogTestInst(line, testName)
        return testInst
           
    
    def __isPassFailEfuse(self,line):
        if ("Fail" in line) or ("Pass" in  line):
            return True
        else:
            return False
    
    
    def __getAnalogTestInst(self,line,testName):
        measName = self.__getAnalogTestname(line)
        pinName = self.__getAnalogPinName(line)
        lowLimit = self.__getLowLimit(line)
        highLimit = self.__getHighLimit(line)
        units = self.__getUnits(line)
        measRslt = self.__getMeasRslt(line)
        if "PINSHORTSTEST" in testName:
            testInst = (testName,"",pinName,lowLimit,measRslt,highLimit,units)
        else:   
            testInst = (testName,"",measName,lowLimit,measRslt,highLimit,units)
        return testInst
    
    
    def __getTestName(self,lineNum):
        #get the first instance that includes this line number
        foundInstance = next((inst for inst in self.__testInstances if inst[LINE_NUM] == lineNum), None)
        testName = foundInstance[TEST_NAME]
        testName = testName.strip()  
        testName = testName[1:-1] #remove "<>" from test name
        return testName
   
    
    def __getLowLimit(self,line):
        lowLimit = line[104:118]
        words = lowLimit.split()
        try:
            lowLimit = words[0]
        except:
            self.doNothing()
        lowLimit = lowLimit.strip()
        lowLimit = lowLimit.upper()
        if lowLimit == "N/A":
            lowLimit = ""
        return lowLimit
   
    
    def __getMeasRslt(self,line):
        measRslt = line[119:138]
        words = measRslt.split()
        try:
            measRslt = words[0]
        except:
            self.doNothing()
        measRslt = measRslt.strip()
        measRslt = measRslt.upper()
        return measRslt
   
    
    def __getUnits(self,line):
        units = line[119:138]
        words = units.split()
        try:
            units = words[1]
            units = units.strip()
            units = units.upper()
        except:
            units = ""
        return units
   
    
    def __getHighLimit(self,line):
        highLimit = line[138:152]
        words = highLimit.split()
        try:
            highLimit = words[0]
        except:
            self.doNothing()
        highLimit = highLimit.strip()
        highLimit = highLimit.upper()
        if highLimit == "N/A":
            highLimit = ""
        return highLimit
   
    
    def __getAnalogPinName(self,line):
        pinName = line[66:94]
        pinName = pinName.strip()
        pinName = pinName.upper()
        return pinName
   
    
    def __getAnalogTestname(self,line):
        testName = line[15:65]
        testName = testName.strip()
        testName = testName.upper()
        if testName[-2:-1] == "_":
            testName = testName[:-2]
        return testName
   
    
    def __getPatternTestInstance(self,line,measName):
        if ".\Patterns\stus2a_cc_strim_base.PAT" in line:
            patName = "STUS2A_CC_STRIM"
            testName = measName
        elif "TN 0   trim_USB2_CC_st  XSus2a_cc_meas_Modified    running core pattern" in line:
            patName = "XSUS2A_CC_MEAS"
            testName = measName
        else:
            words = line.split()
            patName = words[3].strip()
            patName = patName.upper()
            patName =  self.__cleanUpPatternName(patName)
            testName = words[2].strip()
            testName = testName.upper()
            testName = testName[:-2] if testName[-2:-1] == "." else testName
            testName = testName[:-3] if testName[-3:-2] == "." else testName
            testName = "TP_CSIA_HSRX_VTH0_MO_ST" if "HSRXVTH0VCM" in testName else testName
            testName = "TP_CSIA_HSRX_VTH4_MO_ST" if "HSRXVTH4VCM" in testName else testName
            testName = "TP_CSIB_HSRX_VTH1_MO_ST" if "CSIB_V_HSRXVTH1VCM" in testName else testName
            testName = "CSIC_V_HSRXVTH1VCM" if "TP_CSIC_HSRX_VTH1_MO_ST" in testName else testName
            testName = "TP_CSIB_CCP_VTH_MO_ST" if "CSIB_V_CCPVTH" in testName else testName
            testName = "TP_CSIC_CCP_VTH_MO_ST" if "CSIC_V_CCPVTH" in testName else testName
            testName = "TP_CSIA_LPCDH_MO_ST" if "CSIA_V_LPCDVIH" in testName else testName
            testName = "TP_DSIA_LPCDH_MO_ST" if "DSIA_V_LPCDVIH" in testName else testName
            testName = "TP_DSIC_LPCDH_MO_ST" if "DSIC_V_LPCDVIH" in testName else testName
            testName = "TP_CSIA_LPRXL_MO_ST" if "CSIA_V_LPRX" in testName else testName
            testName = "TP_CSIB_LPRXL_MO_ST" if "CSIB_V_LPRX" in testName else testName
            testName = "TP_CSIC_LPRXL_MO_ST" if "CSIC_V_LPRX" in testName else testName
            testName = "TP_DSIC_LPRXL_MO_ST" if "DSIC_V_LPRX" in testName else testName
            testName = "TP_CSIA_ULPRXL_MO_ST" if "CSIA_V_ULPRX" in testName else testName
            testName = "TP_DSIA_ULPRXL_MO_ST" if "DSIA_V_ULPRX" in testName else testName
            testName = "TP_CSIB_ULPRXL_MO_ST" if "CSIB_V_ULPRX" in testName else testName
            testName = "TP_CSIC_ULPRXL_MO_ST" if "CSIC_V_ULPRX" in testName else testName
            testName = "TP_DSIC_ULPRXL_MO_ST" if "DSIC_V_ULPRX" in testName else testName
            testName = "STUS2A_RTERM_STRIM" if "STUS2A_RTERM_STRIM_" in testName else testName
        testInst = (testName,patName,"","","","")
        return testInst
    
    
    def __cleanUpPatternName(self,patternName):
        patName = patternName
        if patternName[-4:] == ".PAT":
            patName = patternName[:-4]
        if patternName == "BOOT_ATPGTEMP":
            patName = "BOOT_ATPG"
        elif patternName[-6:-1] == "_DISC":
            patName = patternName[:-1]
        return patName
        
        
    def __isTestGroupName(self,words):
        #test group names have only one word in line 
        if len(words) != 1: return False          
        words[0].strip()         
        isTestGroupName = True if (words[0][0] == "<") and (words[0][-1] != ">") else False
        return isTestGroupName            
       

    def _isPatternTest(self,line):   
        if  "boot_any" in line:
            self.doNothing()           
        words = line.split()
        if "running core pattern" in line: return True
        elif len(words) != 6: return False
        patName = words[3].upper()
        if "SCAN_MATCH_PASS" in patName: return False
        elif "PMSTOP_MOD" in patName: return False
        elif "P_CON_SLDO_ALL" in patName: return False
        elif "FREQMEASCPUSUBR" in patName: return False
        elif "SRM_LOOP_" in patName: return False
        elif "MEMRETINITBURST" in patName: return False
        elif "LPBK1P5V2" in patName: return False
        elif "IDD_" in patName: return False
        elif "XBHDMA_TXDC_CHAR0" in patName: return False
        elif ".\Patterns\stus2a_cc_strim_base.PAT" in line: return True  
        elif  (words[4].strip() == "N/A") and (words[5].strip() == "N/A"): return True
        else: return False
        
    
    
    def __isAnalogTest(self,line):
        measUnit = self.__getUnits(line)
        measUnits = ["V","MV","UV","A","MA","UA","NA",
                     "Z", "M","U","MHZ","INT"]
        isAnalogTest = True if measUnit in measUnits else False
        return isAnalogTest


#used to test class using runs as 
if __name__ == '__main__':
    uflex = parseUflexDatalogClass()
    testInt = uflex.getTestInstances()
    uflex.doNothing()
