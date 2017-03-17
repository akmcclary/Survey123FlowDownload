#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      amcclary
#
# Created:     16/03/2017
# Copyright:   (c) amcclary 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import ago
import urllib2
import zipfile
import json
import arcpy
import os


def appendSQL(tableName):
    ExistingPt = []
    SQL_fullpath = GDB + tableName
    cursor = arcpy.da.SearchCursor(SQL_fullpath, ["FORMID"]) #will need to change this to "unique field in Master_List (in the SN database this is JoinGPSID)
    for row in cursor:
        FormID = row[0]
        FormID = FormID.strip()
        ExistingPt.append(FormID)
        print ExistingPt
    del cursor


    workspace = os.path.dirname(GDB)  #this block of code opens an editing session to run the update cursor
    edit = arcpy.da.Editor(workspace)
    edit.startEditing(False, True)
    edit.startOperation()

    cursor2 = arcpy.da.UpdateCursor(SQL_fullpath, ["FORMID","TESTEXISTS"]) # iterates through table and populaties Row[1] based on existingpt list
    for row in cursor2:
        value = row[0]
        print value

        if value in ExistingPt:
            print "Found Point"
            row[1] = "Test"
            cursor2.updateRow(row)

        else:
            print "New Point"
            row[1] = "New"
            cursor2.updateRow(row)

    del cursor2


    edit.stopOperation() #this closes the update cursor editing session
    edit.stopEditing(True)

arcpy.env.workspace = "C:/Users/amcclary/Downloads/S123_29e2c18ab9de40cdbd105d84dba9e521_FGDB/14389e11a774439084868d688ba5c172.gdb/"

GDB= "C:/Users/amcclary/Downloads/S123_29e2c18ab9de40cdbd105d84dba9e521_FGDB/14389e11a774439084868d688ba5c172.gdb/"
##MODULE_ClearWorkspaceLocks.clearWSLocks(GDBpath)  #checks for existing locks on GDB
FCS = arcpy.ListFeatureClasses()

Tables = arcpy.ListTables()

FCList = []
TableList= []

for FC in FCS:
    appendSQL(FC)

#for FeatureClass in FeatureClasses:
    #print FeatureClass

for Table in Tables:
    appendSQL(Table)




