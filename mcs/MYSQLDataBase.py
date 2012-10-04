#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012 Jan Kotanski
#
#    nexdatas is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    nexdatas is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with nexdatas.  If not, see <http://www.gnu.org/licenses/>.
## \package mcs nexdatas.configserver
## \file MYSQLDataBase.py
# Allows the access to MYSQL database with NDTS configuration files 
#

import MySQLdb


## XML Configurer
class MYSQLDataBase(object):
    def __init__(self):
        ## XML string
        self.xmlConfig = ""
        self.db = None 

    def connect(self, args):
        print "connect:", args
        db = MySQLdb.connect(**args)


    def close(self):
        db.close()
        print "Close connection"


    def components(self, argin):
        argout = argin
        print "components"
        return argout


    def dataSources(self, argin):
        argout = argin
        print "datasource"
        return argout


    def availableComponents(self):
        argout = ["<xml2>","<xml1>"]
        print "available components"
        return argout



    def availableDataSources(self):
        argout = ["<xml2>","<xml1>"]
        print "available datasources"
        return argout


    def storeComponent(self, argin):
        argout = argin
        print "store component", argin


    def storeDataSource(self, argin):
        argout = argin
        print "store DataSource", argin

    def createConfiguration(self, argin):
        argout = argin
        print "create configuration"


if __name__ == "__main__":

    import time

            
                
    
