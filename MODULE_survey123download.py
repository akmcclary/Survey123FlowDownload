#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      abartshi
#
# Created:     13/01/2017
# Copyright:   (c) abartshi 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import ago
import urllib2
import zipfile
import json
import arcpy
import os


class survey123download:

    def __init__(self, in1, in2):
        self.featureService_ID = in1
        self.download_folder = in2


    def downloadFile(self, url, filename, token):
        """
        Downloads a file from the given URL.
        :param url: URL from which to download the file
        :param filename: Name of file to store the download locally. Proper permissions are assumed.
        :param token: Token for the portal identity
        :return:
        """
        print ("...Downloading")
        req = urllib2.urlopen(url + "?token=" + token)
        CHUNK = 16 * 1024
        with open(filename, 'wb') as fp:
            while True:
                chunk = req.read(CHUNK)
                if not chunk: break
                fp.write(chunk)

    def extractZIP(self,filename,folder):
        """
        Extracts the contents of the zip file into the specified folder.
        :param filename: The name of the ZIP archive to unpack. The file is assumed to exist.
        :param folder: The target folder to hold the content of the ZIP archive. Proper permissions are assumed.
        :return:
        """
        print ("...Extracting")
        zfile = zipfile.ZipFile(filename)
        zfile.extractall(folder)











