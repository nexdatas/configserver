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
## \file XMLConfigurer.py
# Allows the access to a database with NDTS configuration files 
#

from MYSQLDataBase import MYSQLDataBase as MyDB
import json
from Merger import Merger 

## XML Configurer
class XMLConfigurer(object):
    def __init__(self):
        ## XML string
        self.xmlConfig = ""
        self.jsonSettings = "{}"
        self.mydb = MyDB()


    def open(self): 
        args = {}
        print "Open connection"
        try:
            js = json.loads(self.jsonSettings)
            targs = dict(js.items())
            for k in targs.keys():
                args[str(k)] = str(targs[k])
        except:
            args = {}
        self.mydb.connect(args)    
            
            

    def close(self):
        if self.mydb:
            self.mydb.close()    
        print "Close connection"


    def components(self, argin):
        if self.mydb:
            argout = self.mydb.components(argin)   
#        print "components"
        return argout


    def dataSources(self, argin):
        if self.mydb:
            argout = self.mydb.dataSources(argin)   
#        print "datasource"
        return argout


    def availableComponents(self):
        if self.mydb:
            argout = self.mydb.availableComponents()   
        return argout


    def availableDataSources(self):
        if self.mydb:
            argout = self.mydb.availableDataSources()   
        return argout


    def storeComponent(self, argin):
        if self.mydb:
            self.mydb.storeComponent(argin, self.xmlConfig )   


    def storeDataSource(self, argin):
        if self.mydb:
           self.mydb.storeDataSource(argin, self.xmlConfig )   


    def deleteComponent(self, argin):
        if self.mydb:
            self.mydb.deleteComponent(argin)   


    def deleteDataSource(self, argin):
        if self.mydb:
           self.mydb.deleteDataSource(argin)   


    def createConfiguration(self, argin):
        if self.mydb:
            comps = self.mydb.components(argin)   
        mgr = Merger()
        mgr.collect(comps)
        mgr.merge()
        self.xmlConfig = mgr.toString()
        print "create configuration"


if __name__ == "__main__":
    
    import time
    try:
        conf = XMLConfigurer()
        conf.jsonSettings = '{"host":"localhost","db":"ndts","read_default_file":"/etc/my.cnf"}'
        conf.open()
        print conf.availableComponents()
#        conf.createConfiguration(["scan1","scan2"])
        conf.createConfiguration(["scan1","scan1"])
        print conf.xmlConfig
    finally:
        if conf:
            conf.close()
                
    
