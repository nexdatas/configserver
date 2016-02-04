#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2016 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
import nxsconfigserver
from xml import sax
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
    def __init__(self, server=None):
        ## XML config string
        self.xmlstring = ""
        ## component selection
        self.selection = "{}"
        ## JSON string with arguments to connect to database
        self.jsonsettings = "{}"
        ## datasources to be switched into STEP mode
        self.__stepdatasources = "[]"

        ## string with XML variables
        self.variables = "{}"

        ## XML variables
        self.__parameters = {}

        ## instance of MYSQLDataBase
        self.__mydb = MyDB()

        ## datasource label
        self.__dsLabel = "datasources"

        ## variable label
        self.__varLabel = "var"

        ## component label
        self.__cpLabel = "components"

        ## template label
        self.__templabel = '__template__'

        ## delimiter
        self.__delimiter = '.'

        ## version label
        self.versionLabel = "XCS"

        ## Tango server
        self.__server = server

        if server:
            if hasattr(self.__server, "log_fatal"):
                Streams.log_fatal = server.log_fatal
            if hasattr(self.__server, "log_error"):
                Streams.log_error = server.log_error
            if hasattr(self.__server, "log_warn"):
                Streams.log_warn = server.log_warn
            if hasattr(self.__server, "log_info"):
                Streams.log_info = server.log_info
            if hasattr(self.__server, "log_debug"):
                Streams.log_debug = server.log_debug

    ## converts string to json list
    # \param string with list of item or json list
    # \returns json list
    @classmethod
    def __stringToListJson(cls, string):
        if not string or string == "Not initialised":
            return "[]"
        try:
            acps = json.loads(string)
            if not isinstance(acps, (list, tuple)):
                raise AssertionError()
            jstring = string
        except (ValueError, AssertionError):
            lst = re.sub("[:,;]", "  ", string).split()
            jstring = json.dumps(lst)
        return jstring

    ## get method for dataSourceGroup attribute
    # \returns names of STEP dataSources
    def __getStepDatSources(self):
        try:
            lad = json.loads(self.__stepdatasources)
            assert isinstance(lad, list)
            return self.__stepdatasources
        except Exception:
            return '[]'

    ## set method for dataSourceGroup attribute
    # \param names of STEP dataSources
    def __setStepDatSources(self, names):
        jnames = self.__stringToListJson(names)
        ## administator data
        self.__stepdatasources = jnames

    ## the json data string
    stepdatasources = property(
        __getStepDatSources,
        __setStepDatSources,
        doc='step datasource list')

    ## get method for version attribute
    # \returns server and configuration version
    def __getVersion(self):
        version = nxsconfigserver.__version__ + \
            "." + self.versionLabel + "." + self.__mydb.version()
        return version

    ## configuration version
    version = property(__getVersion,
                       doc='configuration version')

    ## opens database connection
    # \brief It opens connection to the give database by JSON string
    def open(self):
        args = {}
        Streams.info("XMLConfigurator::open() - Open connection")
        try:
            js = json.loads(self.jsonsettings)
            targs = dict(js.items())
            for k in targs.keys():
                args[str(k)] = targs[k]
        except:
            Streams.info("%s" % args)
            args = {}
        self.__mydb.connect(args)

    ## closes database connection
    # \brief It closes connection to the open database
    def close(self):
        if self.__mydb:
            self.__mydb.close()
        Streams.info("XMLConfigurator::close() - Close connection")

    ## fetches the required components
    # \param names list of component names
    # \returns list of given components
    def components(self, names):
        argout = []
        if self.__mydb:
            argout = self.__mydb.components(names)
        return argout

    ## fetches the required selections
    # \param names list of selection names
    # \returns list of given selections
    def selections(self, names):
        argout = []
        if self.__mydb:
            argout = self.__mydb.selections(names)
        return argout

    ## instantiates the required components
    # \param names list of component names
    # \returns list of instantiated components
    def instantiatedComponents(self, names):
        comps = []
        if self.__mydb:
            comps = self.__mydb.components(names)
            comps = [self.__instantiate(cp) for cp in comps]
        return comps

    ## instantiates the xml component
    # \param xmlcp xml component
    # \returns instantiated components
    def __instantiate(self, xmlcp):
        return self.__attachVariables(
            self.__attachDataSources(
                self.__attachVariables(
                    self.__attachComponents(
                        xmlcp))))

    ## provides a list of datasources from the given component
    # \param name given component
    # \returns list of datasource names from the given component
    def componentDataSources(self, name):
        cpl = []
        if self.__mydb:
            cpl = self.instantiatedComponents([name])
            if len(cpl) > 0:
                handler = ComponentHandler(self.__dsLabel)
                sax.parseString(str(cpl[0]).strip(), handler)
                return list(handler.datasources.keys())
            else:
                return []

    ## provides a list of datasources from the given components
    # \param names given components
    # \returns list of datasource names from the given components
    def componentsDataSources(self, names):
        mcnf = str(self.merge(names)).strip()
        if mcnf:
            cnf = self.__instantiate(mcnf)
            handler = ComponentHandler(self.__dsLabel)
            sax.parseString(cnf, handler)
            return list(handler.datasources.keys())
        else:
            return []

    ## provides a list of elements from the given text
    # \param text give text
    # \param label element label
    # \returns list of element names from the given text
    def __findElements(self, text, label):
        variables = []
        index = text.find("$%s%s" % (
            label, self.__delimiter))
        while index != -1:
            try:
                subc = re.finditer(
                    r"[\w]+",
                    text[(index + len(label) + 2):]
                ).next().group(0)
            except:
                subc = ""
            name = subc.strip() if subc else ""
            if name:
                variables.append(name)
            index = text.find("$%s%s" % (
                label, self.__delimiter), index + 1)

        return variables

    ## provides a list of variables from the given components
    # \param name given component
    # \returns list of variable names from the given components
    def componentVariables(self, name):
        cpl = []
        if self.__mydb:
            cpl = self.__mydb.components([name])
            if len(cpl) > 0:
                text = str(cpl[0]).strip()
                return list(self.__findElements(text, self.__varLabel))
            else:
                return []

    ## provides a tuple of variables from the given components
    # \param names given components
    # \returns tuple of variable names from the given components
    def componentsVariables(self, names):
        cnf = str(self.merge(names)).strip()
        if cnf:
            return list(self.__findElements(cnf, self.__varLabel))
        else:
            return []

    ## provides dependent components
    # \param names component names to check
    # \param deps dictionery with dependent components
    # \returns list of depending components
    def dependentComponents(self, names, deps=None):
        dps = deps if deps else {}
        for nm in names:
            if nm not in dps:
                dps[nm] = []
                cpl = self.__mydb.components([nm])
                if cpl:
                    dps[nm] = self.__findElements(cpl[0], self.__cpLabel)
                    self.dependentComponents(dps[nm], dps)
        return dps.keys()

    ## fetches the required datasources
    # \param names list of datasource names
    # \returns list of given datasources
    def dataSources(self, names, _=None):
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

    ## fetches the names of available selections
    # \returns list of available selections
    def availableSelections(self):
        argout = []
        if self.__mydb:
            argout = self.__mydb.availableSelections()
        return argout

    ## fetches the names of available datasources
    # \returns list of available datasources
    def availableDataSources(self):
        argout = []
        if self.__mydb:
            argout = self.__mydb.availableDataSources()
        return argout

    ## stores the component from the xmlstring attribute
    # \param name name of the component to store
    def storeComponent(self, name):
        if self.__mydb:
            self.__mydb.storeComponent(name, self.xmlstring)

    ## stores the selection from the xmlstring attribute
    # \param name name of the selection to store
    def storeSelection(self, name):
        if self.__mydb:
            self.__mydb.storeSelection(name, self.selection)

    ## stores the datasource from the xmlstring attribute
    # \param name name of the datasource to store
    def storeDataSource(self, name):
        if self.__mydb:
            self.__mydb.storeDataSource(name, self.xmlstring)

    ## deletes the given component
    # \param name of the component to delete
    def deleteComponent(self, name):
        if self.__mydb:
            self.__mydb.deleteComponent(name)

    ## deletes the given selection
    # \param name of the selection to delete
    def deleteSelection(self, name):
        if self.__mydb:
            self.__mydb.deleteSelection(name)

    ## deletes the given datasource
    # \param name of the datasource to delete
    def deleteDataSource(self, name):
        if self.__mydb:
            self.__mydb.deleteDataSource(name)

    ## sets component datasources according to given dict
    # \param jdict JSON dict of component datasources
    def setComponentDataSources(self, jdict):
        cps = json.loads(jdict)
        avcp = set(self.availableComponents())
        for cpname, dsdict in cps.items():
            if cpname.startswith(self.__templabel):
                tcpname = cpname
                cpname = cpname[len(self.__templabel):]
            else:
                tcpname = self.__templabel + cpname
            print avcp
            if tcpname not in avcp:
                if cpname not in avcp:
                    raise NonregisteredDBRecordError(
                        "The %s %s not registered" % (
                            "component", cpname))
                else:
                    tcomp = self.components([cpname])[0]
                    self.__mydb.storeComponent(tcpname, tcomp)
            else:
                tcomp = self.components([tcpname])[0]
            tcpdss = self.componentDataSources(tcpname)
            self.__parameters = {}
            for tds, ds in dsdict.items():
                if tds not in tcpdss:
                    raise NonregisteredDBRecordError(
                        "The datasource %s absent in the component %s"
                        % (tds, tcpname))
                else:
                    self.__parameters[str(tds)] = "$datasources.%s" % ds
            comp = self.__attachElements(
                tcomp, self.__dsLabel,
                self.__parameters.keys(),
                self.__getParameter, onlyexisting=True)
            self.__mydb.storeComponent(cpname, comp)

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

    def __getVariable(self, name, default=None):
        if len(name) > 0 and name[0] and name[0] in self.__parameters:
            return [self.__parameters[name[0]]]
        elif default is not None:
            return [str(default)]
        else:
            return [""]

    def __getParameter(self, name, default=None):
        if len(name) > 0 and name[0] and name[0] in self.__parameters:
            return [self.__parameters[name[0]]]
        else:
            return []

    ## attaches elements to component
    # \param component given component
    # \param label element label
    # \param keys element names
    # \param funValue function of element value
    # \param tag xml tag
    # \param onlyexisting attachElement only if exists
    # \returns component with attached variables
    def __attachElements(self, component, label, keys, funValue,
                         tag=None, onlyexisting=False):
        index = component.find("$%s%s" % (label, self.__delimiter))
        while index != -1:
            defsubc = None
            subc = ''
            dsubc = ''
            try:
                subc = re.finditer(
                    r"[\w]+",
                    component[(index + len(label) + 2):]).next().group(0)
                if not tag:
                    offset = index + len(subc) + len(label) + 2
                    if component[offset] == '#':
                        if component[offset + 1:offset + 7] == '&quot;':
                            soff = component[(offset + 7):].find('&quot;')
                            dsubc = component[
                                (offset + 1):(offset + 13 + soff)]
                            defsubc = dsubc[6:-6].replace('\\"', '"')
                        elif component[offset + 1:offset + 8] == '\&quot;':
                            soff = component[(offset + 8):].find('\&quot;')
                            dsubc = component[
                                (offset + 1):(offset + 15 + soff)]
                            defsubc = dsubc[7:-7].replace('\\"', '"')
                        else:
                            dsubc = re.finditer(
                                r"([\"'])(?:\\\1|.)*?\1",
                                component[(offset + 1):]).next().group(0)
                            if dsubc:
                                if dsubc[0] == "'":
                                    defsubc = dsubc[1:-1].replace("\\'", "'")
                                elif dsubc[0] == '"':
                                    defsubc = dsubc[1:-1].replace('\\"', '"')
            except:
                pass
            name = subc.strip() if subc else ""
            if name:
                if tag and name not in keys:
                    raise NonregisteredDBRecordError(
                        "The %s %s not registered in the DataBase" % (
                            tag if tag else "variable", name))
                try:
                    xmlds = funValue([name], defsubc)
                except:
                    xmlds = []
                if not onlyexisting and not xmlds:
                    raise NonregisteredDBRecordError(
                        "The %s %s not registered" % (
                            tag if tag else "variable", name))
                if tag:
                    dom = parseString(xmlds[0])
                    domds = dom.getElementsByTagName(tag)
                    if not domds:
                        raise NonregisteredDBRecordError(
                            "The %s %s not registered in the DataBase" % (
                                tag if tag else "variable", name))
                    ds = domds[0].toxml()
                    if not ds:
                        raise NonregisteredDBRecordError(
                            "The %s %s not registered" % (
                                tag if tag else "variable", name))
                    ds = "\n" + ds
                else:
                    ds = xmlds[0] if (xmlds or not onlyexisting) else None
                if xmlds:
                    component = component[0:index] + ("%s" % ds) \
                        + component[
                            (index + len(subc) + len(label) + 2 +
                             ((len(dsubc) + 1)
                              if defsubc is not None else 0)):]
                if not onlyexisting:
                    index = component.find("$%s%s" % (label, self.__delimiter))
                else:
                    index = component.find(
                        "$%s%s" % (label, self.__delimiter),
                        index + 1)
            else:
                raise NonregisteredDBRecordError(
                    "The %s %s not registered" % (
                        tag if tag else "variable", name))
        return component

    ## attaches variables to component
    # \param component given component
    # \returns component with attached variables
    def __attachVariables(self, component):
        if not component:
            return
        self.__parameters = {}
        js = json.loads(self.variables)
        targs = dict(js.items())
        for k in targs.keys():
            self.__parameters[str(k)] = str(targs[k])
        return self.__attachElements(
            component, self.__varLabel,
            self.__parameters.keys(), self.__getVariable)

    ## attaches variables to component
    # \param component given component
    # \returns component with attached variables
    def __attachComponents(self, component):
        if not component:
            return
        return self.__attachElements(
            component, self.__cpLabel, [], lambda x, y: [""])

    ## attaches datasources to component
    # \param component given component
    # \returns component with attached datasources
    def __attachDataSources(self, component):
        if not component:
            return
        return self.__attachElements(
            component, self.__dsLabel,
            self.availableDataSources(), self.dataSources,
            "datasource")

    ## merges the give components
    # \param names list of component names
    # \return merged components
    def merge(self, names):
        return self.__mergeVars(names, False)

    ## merges the give components
    # \param names list of component names
    # \param withVariables if true variables will be substituted
    # \return merged components
    def __mergeVars(self, names, withVariables=False):
        xml = ""
        if self.__mydb:
            allnames = self.dependentComponents(
                list(set(self.__mydb.mandatory() + names)))
            comps = self.__mydb.components(list(set(allnames)))
            if withVariables:
                comps = [self.__attachVariables(cp) for cp in comps]
            xml = self.__merge(comps)
        return xml if xml is not None else ""

    ## merges the give component xmls
    # \param xmls list of component xmls
    # \return merged components
    def __merge(self, xmls):
        mgr = Merger()
        mgr.stepdatasources = json.loads(self.stepdatasources)
        mgr.collect(xmls)
        mgr.merge()
        return mgr.toString()

    ## creates the final configuration string in the xmlstring attribute
    # \param names list of component names
    def createConfiguration(self, names):
        cnf = self.__mergeVars(names, withVariables=True)
        cnf = self.__instantiate(cnf)
        cnfMerged = self.__merge([cnf])

        if cnfMerged and hasattr(cnfMerged, "strip") and cnfMerged.strip():
            reparsed = parseString(cnfMerged)
            self.xmlstring = str((reparsed.toprettyxml(indent=" ", newl="")))
        else:
            self.xmlstring = ''
        Streams.info("XMLConfigurator::createConfiguration() "
                     "- Create configuration")


if __name__ == "__main__":

    try:
        ## configurer object
        conf = XMLConfigurator()
        conf.jsonsettings = '{"host":"localhost", "db":"nxsconfig", '\
            '"read_default_file":"/etc/my.cnf"}'
        conf.open()
        print(conf.availableComponents())
        conf.createConfiguration(["scan2", "scan2", "scan2"])
        print(conf.xmlstring)
    finally:
        if conf:
            conf.close()
