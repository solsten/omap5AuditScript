'''
Created on Feb 6, 2018

@author: andersco
'''
from subModules.compareVlctUflexDatalogsClass import compareVlctUflexDatalogsClass
import argparse


if __name__ == '__main__':
    
    #get file names
    parser = argparse.ArgumentParser()
    parser.add_argument("vlctDatalog", help="VLCT Datalog Filename")
    parser.add_argument("uflexDatalog", help="UFLEX Datalog Filename")
    parser.add_argument("auditFile", default = None, nargs='?', help="Audit File Datalog Filename")
    parser.add_argument("auditFile2", default = None, nargs='?', help="Audit File Datalog Filename")
    args = parser.parse_args()
    
    #compareDatalogs.parseTestInstFile("Inst_Analog_FT1.txt")
    print("")
    print("please be patient, this script may take a couple of minutes")
    print("")
    compareDatalogs = compareVlctUflexDatalogsClass()    
    print("parsing "  + args.vlctDatalog + "...")
    compareDatalogs.parseVlctDatalog(args.vlctDatalog)
    print("parsing "  + args.uflexDatalog + "...")
    compareDatalogs.parseUflexDatalog(args.uflexDatalog)
    if args.auditFile:
        print("parsing "  + args.auditFile + "...")
        compareDatalogs.parseAuditFile(args.auditFile)
    if args.auditFile2:
        print("parsing "  + args.auditFile2 + "...")
        compareDatalogs.parseAuditFile(args.auditFile2)
    print("comparing "  + args.vlctDatalog + " and "+ args.uflexDatalog + "...")
    compareDatalogs.comparePatterns()
    compareDatalogs.compareAnalogTests()
    #compareDatalogs.compareContinuityTests()
    print("Saving results to workbook...")
    compareDatalogs.saveWorkbook()
    print("Done")
