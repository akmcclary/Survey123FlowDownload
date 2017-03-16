#-------------------------------------------------------------------------------
# Name:        survey123download class
# Purpose:  This script is designed to be called from ESRI modelbuilder with a user selected survey from pre-populated choices.
#         The script will then download the selected survey data (as a geodatabase) from ESRI AGOL servers to a temporary local
#         folder. The downloaded FC will then be compared to the equivelant dataset stored in SQL server and only records not matching
#         existing records in the SQL table will be selected, then appeneded into the SQL table. The temp geodatabase is then deleted.
#	  This script is based on "DownloadSurvey123Data" script found at http://survey123.maps.arcgis.com/home/item.html?id=c8411764ea614f208ba2e5a933a068b8
#
# Author:      Andrew Bartshire
#
# Created:     01/13/2017
# Copyright:   (c) Andrew Bartshire 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------


import ago
import urllib2
import zipfile
import json
import arcpy
import os
import MODULE_ClearWorkspaceLocks
import MODULE_survey123download  #this module has the functions used to actually execute the survey123 download. 

dict = {'Form_FieldReconID':'d20962458324416ea077215b8c7b0827', 'Form_FieldReconPATH' : 'S:\Coho\GIS\Data\Survey123_Downloads\Form_FieldRecon',
        'DissolvedOxygenID': '34ec889e9cf04e098b6589855e2a67c0', 'DissolvedOxygenPATH': 'S:\Coho\GIS\Data\Survey123_Downloads\WH_DissolvedOxygen',
        'MouthCheckID':'d2fd2fc1cd664db08dcceab4a95887b3', 'MouthCheckPATH' : 'S:\Coho\GIS\Data\Survey123_Downloads\MouthChecks',
        'TempLoggerID':'492e5d2a874640c59b4821c58a1bbd65', 'TempLoggerPATH' : 'S:\Coho\GIS\Data\Survey123_Downloads\TempLoggers',
        'NFWFConnectivityID':'a8cebf27c0414eb7b2b4084c8b3dfde5', 'NFWFConnectivityPATH' : 'S:\Coho\GIS\Data\Survey123_Downloads\WH_NFWFConnectivity',
        'ThalwegID':'a59ff07fb4aa422592cd31959e571780', 'ThalwegPATH' : 'S:\Coho\GIS\Data\Survey123_Downloads\WH_Thalweg',
        'Download_TestID':'44ec578f8afa490fbb35e38a63287c9d', 'Download_TestPATH' : r'S:\Coho\GIS\Data\Survey123_Downloads\DownloadTest',}
#Dictionary of AGOL Id's and corresponding network paths for survey123 forms. This dictionary needs to be updated as forms are added or
#changed. Make sure ********ID and ********PATH match eachother and also match the parameter (input_survey) being passed from GIS tool and the form name on AGOL.

GDBpath = ""  #defining global variable for listdir search later


#input_survey = arcpy.GetParameterAsText(0)  #use if calling from modelbuilder tool
input_survey = "Form_FieldRecon"  #for local testing

#survey is variable that is populated based on parameter defined by user input in GIS tool

parID = dict[input_survey + "ID"]
parPATH= dict[input_survey + "PATH"]
#defines variables to be passed through as inputs for module
#gdbNAME = dict[input_survey + "PATH"] + '\\' + input_survey
#gdbNAME= str(gdbNAME)
folderpath= dict[input_survey + "PATH"] + '\\'

run = MODULE_survey123download.survey123download(parID, parPATH)

download_file = run.download_folder + 'download.zip'
# ArcGIS user credentials to authenicate against the portal
credentials = { 'userName' : 'abartshire_ucce', 'passWord' : 'A111111.'}
# Address of your ArcGIS portal
portal_url = r"http://sonomamap.maps.arcgis.com/"
# Output format  Shapefile | CSV | File Geodatabase
output_format = 'File Geodatabase'
local_featureServiceID = run.featureService_ID

######################## START OF NESTED SCRIPT ##################################


print ("...Starting")
# initialize the portal helper class
# ago.py is part of the 10.3 python install
agol_helper = ago.AGOLHelper(portal_url)
print ("...Authenticating against your Portal ")
# login
agol_helper.login(credentials['userName'], credentials['passWord'])

# export url and parameters
export_url = "{}/content/users/{}/export".format(agol_helper.secure_url, agol_helper.username)

export_parameters = {
    'token': agol_helper.token,
    'itemId': local_featureServiceID,
    'title': "Temp-" + str(int(round(time.time() * 1000))),
    'exportFormat': output_format,
    'f' :'json'
}
# launching async export request
export_data = agol_helper.url_request(export_url, export_parameters, request_type="POST")

if export_data is  None:
    print "ERROR: Can't find a feature service with id: " + local_featureServiceID
    print "TIP:   Navigate to the item details page of your feature service, and get the id from the URL"
else:
    print ("...Exporting data")
    # retrieve the itemId for the export
    exportItemId = export_data['exportItemId']
    # retrieve the jobId to watch the export progress
    jobId = export_data['jobId']
    status = "processing"

    items_url = "{}/content/users/{}/items/{}/status".format(agol_helper.secure_url,agol_helper.username, exportItemId)
    data_url = "{}/content/items/{}/data".format(agol_helper.secure_url, exportItemId)

    status_parameters = {
        'jobId' : jobId,
        'jobType' : 'export',
        'f' : 'json',
        'token' : agol_helper.token
    }

    while status == "processing":
        print ("...." + status)
        # checking export job status
        time.sleep(5)
        data = agol_helper.url_request(items_url, status_parameters)

        status = data['status']

    if status == "completed":
        print ("...." + status)
        # once the export has completed, download the file
        run.downloadFile(data_url, download_file, agol_helper.token)
        # deleting export results in the portal
        agol_helper.delete(item_id=export_data['exportItemId'])
        # uncompress the contents of the archive
        run.extractZIP(download_file, run.download_folder)


    else:
        raise Exception("!!! Export job failed. Status \"" + status + "\"")

    print ("Completed. Files available at: " + run.download_folder)


################# END OF NESTED SCRIPT ###########################################

for file in os.listdir(parPATH):  #searches through survey folder for downloaded GDB and assignes the name to GDBname variable.
    if file.endswith(".gdb"):
        GDBname = file
    else:
        pass

GDBpath = folderpath + GDBname #string of path to GDB

FC_GDB = GDBpath + '\\' + input_survey  #string of full path for feature class within GDB

SQL_Shortcut= r"Database Connections\SQL_Temporary.sde\UCCE_Temporary_SQL.dbo."

SQL_fullpath= SQL_Shortcut + input_survey

MODULE_ClearWorkspaceLocks.clearWSLocks(GDBpath)  #checks for existing locks on GDB

ExistingPt = []  #list used to received FORMID values for SQL tbl

cursor = arcpy.da.SearchCursor(SQL_fullpath, ["FORMID"]) #will need to change this to "unique field in Master_List (in the SN database this is JoinGPSID)
for row in cursor:
    FormID = row[0]
    FormID = FormID.strip()
    ExistingPt.append(FormID)
    print ExistingPt
del cursor


workspace = os.path.dirname(FC_GDB)  #this block of code opens an editing session to run the update cursor
edit = arcpy.da.Editor(workspace)
edit.startEditing(False, True)
edit.startOperation()

cursor2 = arcpy.da.UpdateCursor(FC_GDB, ["FORMID","TESTEXISTS"]) # iterates through table and populaties Row[1] based on existingpt list
for row in cursor2:
    value = row[0]
    print value

    if value in ExistingPt:
        print "Found Point"
        row[1] = "Exists"
        cursor2.updateRow(row)

    else:
        print "New Point"
        row[1] = "New"
        cursor2.updateRow(row)

del cursor2


edit.stopOperation() #this closes the update cursor editing session
edit.stopEditing(True)

select_table= arcpy.MakeTableView_management(FC_GDB, 'table_view_from_GDB', '"TESTEXISTS" = \'New\'', GDBpath) #creates temporary tbl view in GDB from FC_GDB w/ only records that have "New" in "TESTEXISTS"

arcpy.Append_management(select_table, SQL_fullpath, "NO_TEST","","") #appends tbl view data into SQL table

arcpy.Delete_management(select_table) #deletes temp tbl view

arcpy.SetParameter(1, "True") #output parameter boolean value for modelbuilder

arcpy.Delete_management(GDBpath) #deletes GDB in survey specific folder, so tool will run next time.


##### .csv files bring down the label name for field names (spaces and other characters included) downloading a file geodatabase
##### resolves this problem but the download tool for file geodatabase autopopulates a new "globalID" as the GDB name. I still need to
##### figure out how to have script find the gdb location automatically even with the globalID.