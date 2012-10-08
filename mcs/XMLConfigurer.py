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
    ## constructor
    # \brief It allows to construct XML configurer object
    def __init__(self):
        ## XML config string
        self.xmlConfig = ""
        ## JSON string with arguments to connect to database
        self.jsonSettings = "{}"
        ## names of mandatory components 
        self._mandatory = []

        self._mydb = MyDB()

    ## opens database connection
    # \brief It opens connection to the give database by JSON string
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
        self._mydb.connect(args)    
            
            

    ## closes database connection
    # \brief It closes connection to the open database
    def close(self):
        if self._mydb:
            self._mydb.close()    
        print "Close connection"


    ## fetches the required components
    # \param names list of component names
    # \returns list of given components
    def components(self, names):
        if self._mydb:
            argout = self._mydb.components(names)   
        return argout


    ## fetches the required datasources
    # \param names list of datasource names
    # \returns list of given datasources
    def dataSources(self, names):
        if self._mydb:
            argout = self._mydb.dataSources(names)   
        return argout


    ## fetches the names of available components
    # \returns list of available components
    def availableComponents(self):
        if self._mydb:
            argout = self._mydb.availableComponents()   
        return argout


    ## fetches the names of available datasources
    # \returns list of available datasources
    def availableDataSources(self):
        if self._mydb:
            argout = self._mydb.availableDataSources()   
        return argout


    ## stores the component from the xmlConfig attribute
    # \param name of the component to store
    def storeComponent(self, name):
        if self._mydb:
            self._mydb.storeComponent(name, self.xmlConfig )   


    ## stores the datasource from the xmlConfig attribute
    # \param name of the datasource to store
    def storeDataSource(self, name):
        if self._mydb:
           self._mydb.storeDataSource(name, self.xmlConfig )   


    ## deletes the given component
    # \param name list of the component to delete
    def deleteComponent(self, name):
        if self._mydb:
            self._mydb.deleteComponent(name)   


    ## deletes the given datasource 
    # \param name list of the datasource to delete
    def deleteDataSource(self, name):
        if self._mydb:
           self._mydb.deleteDataSource(name)   


    ## sets the mandatory components
    # \param names list of component names
    def setMandatoryComponents(self, names):
        self._mandatory = []
        for name in names:
            self._mandatory.append(name)


    ## Provides names of the mandatory components
    # \returns mandatory components
    def mandatoryComponents(self):
        argout = []
        for name in self._mandatory:
            argout.append(name)
        return argout    


    ## creates the final configuration string in the xmlConfig attribute
    # \param names list of component names
    # \returns list of given components
    def createConfiguration(self, names):
        if self._mydb:
            comps = self._mydb.components(list(set(self._mandatory + names)))   
        print "Components:",comps    
        mgr = Merger()
        mgr.collect(comps)
        mgr.merge()
        self.xmlConfig = mgr.toString()
        print "create configuration"


if __name__ == "__main__":
    
    import time
    try:
        ## configurer object
        conf = XMLConfigurer()
        conf.jsonSettings = '{"host":"localhost","db":"ndts","read_default_file":"/etc/my.cnf"}'
        conf.open()
        print conf.availableComponents()
#        conf.createConfiguration(["scan1","scan2"])
#        conf.createConfiguration(["scan1","scan1"])
        conf.createConfiguration(["scan2","scan2","scan2"])
        print conf.xmlConfig
    finally:
        if conf:
            conf.close()
                
    
