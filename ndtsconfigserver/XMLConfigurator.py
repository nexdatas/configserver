#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2013 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
## \file XMLConfigurator.py
# Allows the access to a database with NDTS configuration files 
#

from MYSQLDataBase import MYSQLDataBase as MyDB
from ComponentParser import ComponentHandler
import json
from xml import  sax
from xml.dom.minidom import parseString
from Merger import Merger 
from Errors import NonregisteredDBRecordError


## XML Configurator
class XMLConfigurator(object):
    ## constructor
    # \brief It allows to construct XML configurer object
    def __init__(self):
        ## XML config string
        self.xmlConfig = ""
        ## JSON string with arguments to connect to database
        self.jsonSettings = "{}"

        self.__mydb = MyDB()

        self.__dsLabel = "datasources"

    ## opens database connection
    # \brief It opens connection to the give database by JSON string
    def open(self): 
        args = {}
        print "Open connection"
        try:
            js = json.loads(self.jsonSettings)
            targs = dict(js.items())
            for k in targs.keys():
                args[str(k)] = targs[k]
        except:
            print args
            args = {}
        self.__mydb.connect(args)    
            
            

    ## closes database connection
    # \brief It closes connection to the open database
    def close(self):
        if self.__mydb:
            self.__mydb.close()    
        print "Close connection"


    ## fetches the required components
    # \param names list of component names
    # \returns list of given components
    def components(self, names):
        argout = []
        if self.__mydb:
            argout = self.__mydb.components(names)   
        return argout


    ## provides a tuple of datasources from the given component
    # \param name given component 
    # \returns tuple of datasource names from the given component
    def componentDataSources(self, name):
        cpl = []
        if self.__mydb:
            cpl = self.__mydb.components([name])   
            if len(cpl)>0:
                handler = ComponentHandler(self.__dsLabel)
                sax.parseString(str(cpl[0]).strip(), handler)
                return tuple(handler.datasources.keys())


    ## fetches the required datasources
    # \param names list of datasource names
    # \returns list of given datasources
    def dataSources(self, names):
        argout = []
        if self.__mydb:
            argout = self.__mydb.dataSources(names)   
        return argout


    ## fetches the names of available components
    # \returns list of available components
    def availableComponents(self):
        argout = []
        if self.__mydb:
            argout = self.__mydb.availableComponents()   
        return argout


    ## fetches the names of available datasources
    # \returns list of available datasources
    def availableDataSources(self):
        argout = []
        if self.__mydb:
            argout = self.__mydb.availableDataSources()   
        return argout


    ## stores the component from the xmlConfig attribute
    # \param name name of the component to store
    def storeComponent(self, name):
        if self.__mydb:
            self.__mydb.storeComponent(name, self.xmlConfig )   


    ## stores the datasource from the xmlConfig attribute
    # \param name name of the datasource to store
    def storeDataSource(self, name):
        if self.__mydb:
           self.__mydb.storeDataSource(name, self.xmlConfig )   


    ## deletes the given component
    # \param name of the component to delete
    def deleteComponent(self, name):
        if self.__mydb:
            self.__mydb.deleteComponent(name)   


    ## deletes the given datasource 
    # \param name of the datasource to delete
    def deleteDataSource(self, name):
        if self.__mydb:
           self.__mydb.deleteDataSource(name)   


    ## sets the mandtaory components
    # \param names list of component names
    def setMandatoryComponents(self, names):
        for name in names:
            self.__mydb.setMandatory(name)
                


    ## sets the mandatory components
    # \param names list of component names
    def unsetMandatoryComponents(self, names):
        for name in names:
            self.__mydb.unsetMandatory(name)


    ## Provides names of the mandatory components
    # \returns mandatory components
    def mandatoryComponents(self):
        argout = []
        if self.__mydb:
            argout = self.__mydb.mandatory()   
        return argout


    ## creates the final configuration string in the xmlConfig attribute
    # \param names list of component names
    # \returns list of given components
    def createConfiguration(self, names):
        if self.__mydb:
            comps = self.__mydb.components(list(set(self.__mydb.mandatory() + names)))   
        print "CCON", comps 
        mgr = Merger()
        mgr.collect(comps)
        mgr.merge()
        cnf = mgr.toString()
        print "CNF", cnf 
        cnfWithDS = self.__attachDataSources(cnf)
#        self.xmlConfig = cnfWithDS
        if cnfWithDS and hasattr(cnfWithDS,"strip") and  cnfWithDS.strip():
            reparsed = parseString(cnfWithDS)
            self.xmlConfig = str((reparsed.toprettyxml(indent=" ",newl=""))
                                 ).replace("\n \n "," ").replace("\n\n","\n")
        else:
            self.xmlConfig = None
        print "create configuration"



    ## attaches datasrouces to component
    # \param component given component
    # \returns component with attached datasources
    def __attachDataSources(self, component):
        print "COMP", component
        if not component:
            return
        index = component.find("$%s." % self.__dsLabel)
        dsources = self.availableDataSources()
        while index != -1:
            subc = (component[(index+len(self.__dsLabel)+2):].split("<", 1))
            name = subc[0].strip() if subc else None
            print "DS NAME", name
            if name and name in dsources:
                xmlds = self.dataSources([name])
                print "DS XML", xmlds
                if not xmlds:
                    raise NonregisteredDBRecordError, "DataSource %s not registered in the database" % name                    
                dom = parseString(xmlds[0])
                domds = dom.getElementsByTagName("datasource")
                ds = dom.toxml()
                print "PURE DS XML", ds
                if ds:
                    component = component.replace("$%s.%s" % (self.__dsLabel, name),"\n%s" % ds[0])
                    print "COMP2", component
                    index = component.find("$%s." % self.__dsLabel, index)
                else:
                    raise NonregisteredDBRecordError, "DataSource %s not registered in the database" % name
            else:
                raise NonregisteredDBRecordError, "DataSource %s not registered in the database" % name
                
        print "COMP", component
        return component

if __name__ == "__main__":
    
    import time
    try:
        ## configurer object
        conf = XMLConfigurator()
        conf.jsonSettings = '{"host":"localhost", "db":"ndts", "read_default_file":"/etc/my.cnf"}'
        conf.open()
        print conf.availableComponents()
#        conf.createConfiguration(["scan1", "scan2"])
#        conf.createConfiguration(["scan1", "scan1"])
        conf.createConfiguration(["scan2", "scan2", "scan2"])
        print conf.xmlConfig
    finally:
        if conf:
            conf.close()
                
    
