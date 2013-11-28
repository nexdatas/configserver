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

""" Provides the access to a database with NDTS configuration files """

import json
import re
import ndtsconfigserver
from xml import  sax
from xml.dom.minidom import parseString
from .MYSQLDataBase import MYSQLDataBase as MyDB
from .ComponentParser import ComponentHandler
from .Merger import Merger 
from .Errors import NonregisteredDBRecordError
from . import Streams


## XML Configurator
class XMLConfigurator(object):
    ## constructor
    # \brief It allows to construct XML configurer object
    def __init__(self, server = None):
        ## XML config string
        self.xmlConfig = ""
        ## JSON string with arguments to connect to database
        self.jsonSettings = "{}"

        ## string with XML variables
        self.variables = "{}"
        
        ## XML variables
        self.__variables = {}
        
        self.__mydb = MyDB()

        self.__dsLabel = "datasources"

        self.__varLabel = "var"
        
        ## version label
        self.versionLabel = "XCS"

        ## Tango server
        self.__server = server

        if server:
            if  hasattr(self.__server, "log_fatal"):
                Streams.log_fatal = server.log_fatal
            if  hasattr(self.__server, "log_error"):
                Streams.log_error = server.log_error
            if  hasattr(self.__server, "log_warn"):
                Streams.log_warn = server.log_warn
            if  hasattr(self.__server, "log_info"):
                Streams.log_info = server.log_info
            if  hasattr(self.__server, "log_debug"):
                Streams.log_debug = server.log_debug

    
    ## get method for version attribute
    # \returns server and configuration version
    def __getVersion(self):
        version = ndtsconfigserver.__version__ + \
            "." + self.versionLabel + "." + self.__mydb.version() 
        return version

    ## the json data string
    version = property(__getVersion)


    ## opens database connection
    # \brief It opens connection to the give database by JSON string
    def open(self): 
        args = {}
        if Streams.log_info:
            print >> Streams.log_info , \
                "XMLConfigurator::open() - Open connection"
        else:  
            print "XMLConfigurator::open() - Open connection"
        try:
            js = json.loads(self.jsonSettings)
            targs = dict(js.items())
            for k in targs.keys():
                args[str(k)] = targs[k]
        except:
            if Streams.log_info:
                print >> Streams.log_info , "XMLConfigurator::open() - ", \
                    args
            print args
            args = {}
        self.__mydb.connect(args)    
            
            

    ## closes database connection
    # \brief It closes connection to the open database
    def close(self):
        if self.__mydb:
            self.__mydb.close()    
        if Streams.log_info:
            print >> Streams.log_info , \
                "XMLConfigurator::close() - Close connection"
        else:    
            print "XMLConfigurator::close() - Close connection"


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

    def __getVariable(self, name):
        if len(name)>0 and name[0] and name[0] in self.__variables:
            return [self.__variables[name[0]]]
        else:
            return []


    ## attaches variables to component
    # \param component given component
    # \param label element label
    # \param keys element names
    # \param funValue function of element value    
    # \param tag xml tag
    # \returns component with attached variables
    def __attachElement(self, component, label, keys, funValue, tag = None):
        
        index = component.find("$%s." % label)
        while index != -1:
            subc = re.finditer(
                r"[\w]+", 
                component[(index+len(label)+2):]).next().group(0)
            name = subc.strip() if subc else ""
            print "name '%s'" % name , keys 
            if name and name in keys:
                xmlds = funValue([name])
                if not xmlds:
                    raise NonregisteredDBRecordError, \
                        "The %s %s not registered" % (
                        tag if tag else "variable", name)
                if tag:
                    dom = parseString(xmlds[0])
                    domds = dom.getElementsByTagName(tag)
                    if not domds:
                        raise NonregisteredDBRecordError, \
                            "The %s %s not registered in the DataBase" % (
                        tag if tag else "variable", name)
                    ds = domds[0].toxml()
                else:
                    ds = xmlds[0]    
                if ds:
                    if tag:
                        ds = "\n" + ds
                    component = component[0:index] + ("%s" % ds) \
                        + component[(index+len(subc)+len(label)+2):]
                    index = component.find("$%s." % label)
                else:
                    raise NonregisteredDBRecordError, \
                        "The %s %s not registered" % (
                        tag if tag else "variable", name)
            else:
                    raise NonregisteredDBRecordError, \
                        "The %s %s not registered" % (
                        tag if tag else "variable", name)
                
        return component
        


    ## attaches variables to component
    # \param component given component
    # \returns component with attached variables
    def __attachVariables(self, component):
        if not component:
            return
        self.__variables = {}
        js = json.loads(self.variables)
        targs = dict(js.items())
        for k in targs.keys():
            self.__variables[str(k)] = str(targs[k])
        return self.__attachElement(
            component, self.__varLabel, 
            self.__variables.keys(), self.__getVariable)   
                

    ## attaches datasources to component
    # \param component given component
    # \returns component with attached datasources
    def __attachDataSources(self, component):
        if not component:
            return
        return self.__attachElement(
            component, self.__dsLabel, 
            self.availableDataSources(), self.dataSources, 
            "datasource")   
                
        return component

    ## creates the final configuration string in the xmlConfig attribute
    # \param names list of component names
    # \returns list of given components
    def createConfiguration(self, names):
        if self.__mydb:
            comps = self.__mydb.components(list(set(self.__mydb.mandatory() 
                                                    + names)))   
        mgr = Merger()
        mgr.collect(comps)
        mgr.merge()
        cnf = mgr.toString()
        cnfWithDS = self.__attachDataSources(cnf)
        cnfWithVar = self.__attachVariables(cnfWithDS)
        if cnfWithVar and hasattr(cnfWithVar,"strip") and  cnfWithVar.strip():
            reparsed = parseString(cnfWithVar)
            self.xmlConfig = str((reparsed.toprettyxml(indent=" ", newl="")))
        else:
            self.xmlConfig = ''
        if Streams.log_info:
            print >> Streams.log_info , \
                "XMLConfigurator::createConfiguration() " \
                "- Create configuration"
        else:    
            print "XMLConfigurator::createConfiguration() - " \
                "Create configuration"




if __name__ == "__main__":
    
    try:
        ## configurer object
        conf = XMLConfigurator()
        conf.jsonSettings = '{"host":"localhost", "db":"ndts", '\
            '"read_default_file":"/etc/my.cnf"}'
        conf.open()
        print conf.availableComponents()
#        conf.createConfiguration(["scan1", "scan2"])
#        conf.createConfiguration(["scan1", "scan1"])
        conf.createConfiguration(["scan2", "scan2", "scan2"])
        print conf.xmlConfig
    finally:
        if conf:
            conf.close()
                
    
