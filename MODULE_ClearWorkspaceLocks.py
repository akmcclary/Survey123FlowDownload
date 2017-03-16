#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      abartshi
#
# Created:     14/02/2017
# Copyright:   (c) abartshi 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import arcpy


def clearWSLocks(inputWS):
  if not all([arcpy.Exists(inputWS), arcpy.Compact_management(inputWS), arcpy.Exists(inputWS)]):
    print 'Error with Workspace (%s), killing script...' % inputWS
    exit()
  else:
    print "No locks"
    return True


