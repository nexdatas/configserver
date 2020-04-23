#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2017 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
#

""" Provides the access to a database with NDTS configuration files """

import json
import re
import sys
import weakref
from xml import sax
import xml.etree.ElementTree as et
from lxml.etree import XMLParser
from lxml import etree

from .MYSQLDataBase import MYSQLDataBase as MyDB
from .ComponentParser import ComponentHandler
from .Merger import Merger
from .Errors import NonregisteredDBRecordError, WrongXMLError, WrongJSONError
from .Release import __version__
from .StreamSet import StreamSet


def _tostr(text):
    """ converts text  to str type

    :param text: text
    :type text: :obj:`bytes` or :obj:`unicode`
    :returns: text in str type
    :rtype: :obj:`str`
    """
    if isinstance(text, str):
        return text
    elif sys.version_info > (3,):
        return str(text, encoding="utf8")
    else:
        return str(text)


def _toxml(node):
    """ provides xml content of the whole node

    :param node: DOM node
    :type node: :class:`xml.dom.Node`
    :returns: xml content string
    :rtype: :obj:`str`
    """
    xml = _tostr(et.tostring(node, encoding='utf8', method='xml'))
    if xml.startswith("<?xml version='1.0' encoding='utf8'?>"):
        xml = str(xml[38:])
    return xml


class XMLConfigurator(object):

    """ XML Configurator
    """

    def __init__(self, server=None):
        """ constructor

        :param server: NXSConfigServer instance
        :type server: :class:`PyTango.Device_4Impl`
        :brief: It allows to construct XML configurer object

        """
        #: (:class:`StreamSet` or :class:`PyTango.Device_4Impl`) stream set
        self._streams = StreamSet(weakref.ref(server) if server else None)
        #: (:obj:`str`) XML config string
        self.xmlstring = ""
        #: (:obj:`str`) component selection
        self.selection = "{}"
        #: (:obj:`str`) JSON string with arguments to connect to database
        self.jsonsettings = "{}"
        #: (:obj:`str`) datasources to be switched into STEP mode
        self.__stepdatasources = "[]"
        #: (:obj:`str`) datasources to which links will be added
        self.__linkdatasources = "[]"
        #: (:obj:`str`) datasources to be switched into CanFail mode
        self.__canfaildatasources = "[]"

        #: (:obj:`str`) string with XML variables
        self.variables = "{}"

        #: (:obj:`str`) XML variables
        self.__parameters = {}

        #: (:class:`nxsconfigserver.MYSQLDataBase.MYSQLDataBase`) \
        #:        instance of MYSQLDataBase
        self.__mydb = MyDB(streams=self._streams)

        #: (:obj:`str`) datasource label
        self.__dsLabel = "datasources"

        #: (:obj:`str`) variable label
        self.__varLabel = "var"

        #: (:obj:`str`) component label
        self.__cpLabel = "components"

        #: (:obj:`str`) template label
        self.__templabel = '__template__'

        #: (:obj:`str`) delimiter
        self.__delimiter = '.'

        #: (:obj:`str`) version label
        self.versionLabel = "XCS"

        #: (:class:`PyTango.Device_4Impl`) Tango server
        self.__server = server

    @classmethod
    def __stringToListJson(cls, string):
        """ converts string to json list

        :param string: with list of item or json list
        :type string: :obj:`str`
        :returns: json list
        :rtype: :obj:`str`
        """
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

    def __getStepDatSources(self):
        """ get method for dataSourceGroup attribute

        :returns: names of STEP dataSources
        :rtype: :obj:`str`
        """
        try:
            lad = json.loads(self.__stepdatasources)
            assert isinstance(lad, list)
            return self.__stepdatasources
        except Exception:
            return '[]'

    def __setStepDatSources(self, names):
        """ set method for dataSourceGroup attribute

        :param names: of STEP dataSources
        :type names: :obj:`str`
        """
        jnames = self.__stringToListJson(names)
        #: administator data
        self.__stepdatasources = jnames

    #: (:obj:`str`) the json data string
    stepdatasources = property(
        __getStepDatSources,
        __setStepDatSources,
        doc='step datasource list')

    def __getLinkDatSources(self):
        """ get method for dataSourceGroup attribute

        :returns: names of LINK dataSources
        :rtype: :obj:`str`
        """
        try:
            lad = json.loads(self.__linkdatasources)
            assert isinstance(lad, list)
            return self.__linkdatasources
        except Exception:
            return '[]'

    def __setLinkDatSources(self, names):
        """ set method for dataSourceGroup attribute

        :param names: of LINK dataSources
        :type names: :obj:`str`
        """
        jnames = self.__stringToListJson(names)
        #: administator data
        self.__linkdatasources = jnames

    #: (:obj:`str`) the json data string
    linkdatasources = property(
        __getLinkDatSources,
        __setLinkDatSources,
        doc='link datasource list')

    def __getCanFailDatSources(self):
        """ get method for dataSourceGroup attribute

        :returns: names of CanFail dataSources
        :rtype: :obj:`str`
        """
        try:
            lad = json.loads(self.__canfaildatasources)
            assert isinstance(lad, list)
            return self.__canfaildatasources
        except Exception:
            return '[]'

    def __setCanFailDatSources(self, names):
        """ set method for dataSourceGroup attribute

        :param names: of CanFail dataSources
        :type names: :obj:`str`
        """
        jnames = self.__stringToListJson(names)
        #: administator data
        self.__canfaildatasources = jnames

    #: (:obj:`str`) the json data string
    canfaildatasources = property(
        __getCanFailDatSources,
        __setCanFailDatSources,
        doc='canfail datasource list')

    def __getVersion(self):
        """ get method for version attribute

        :returns: server and configuration version
        :rtype: :obj:`str`
        """
        version = __version__ + \
            "." + self.versionLabel + "." + (
                self.__mydb.version() or "<DB_NOT_CONNECTED>"
            )
        return version

    #: (:obj:`str`)configuration version
    version = property(__getVersion,
                       doc='configuration version')

    def open(self):
        """ opens database connection

        :brief: It opens connection to the give database by JSON string
        """
        args = {}
        self._streams.info("XMLConfigurator::open() - Open connection")
        try:
            js = json.loads(self.jsonsettings)
            targs = dict(js.items())
            for k in targs.keys():
                args[str(k)] = targs[k]
        except Exception:
            self._streams.info("%s" % args)
            args = {}
        self.__mydb.connect(args)

    def close(self):
        """ closes database connection

        :brief: It closes connection to the open database
        """

        if self.__mydb:
            self.__mydb.close()
        self._streams.info("XMLConfigurator::close() - Close connection")

    def components(self, names):
        """ fetches the required components

        :param names: list of component names
        :type names: :obj:`list` <:obj:`str`>
        :returns: list of given components
        :rtype: :obj:`list` <:obj:`str`>
        """
        argout = []
        if self.__mydb:
            argout = self.__mydb.components(names)
        return argout

    def selections(self, names):
        """ fetches the required selections

        :param names: list of selection names
        :type names: :obj:`list` <:obj:`str`>
        :returns: list of given selections
        :rtype: :obj:`list` <:obj:`str`>
        """
        argout = []
        if self.__mydb:
            argout = self.__mydb.selections(names)
        return argout

    def instantiatedComponents(self, names):
        """ instantiates the required components

        :param names: list of component names
        :type names: :obj:`list` <:obj:`str`>
        :returns: list of instantiated components
        :rtype: :obj:`list` <:obj:`str`>
        """
        comps = []
        if self.__mydb:
            comps = self.__mydb.components(names)
            comps = [self.__instantiate(cp) for cp in comps]
        return comps

    def __instantiate(self, xmlcp):
        """ instantiates the xml component

        :param xmlcp: xml component
        :type xmlcp: :obj:`str`
        :returns: instantiated components
        :rtype: :obj:`str`

        """
        return self.__attachVariables(
            self.__attachDataSources(
                self.__attachVariables(
                    self.__attachComponents(
                        xmlcp))))

    def componentDataSources(self, name):
        """ provides a list of datasources from the given component

        :param name: given component
        :type name: :obj:`str`
        :returns: list of datasource names from the given component
        :rtype: :obj:`list` <:obj:`str`>
        """
        cpl = []
        if self.__mydb:
            cpl = self.instantiatedComponents([name])
            if len(cpl) > 0:
                handler = ComponentHandler(self.__dsLabel)
                text = str(cpl[0]).strip()
                if sys.version_info > (3,):
                    sax.parseString(bytes(text, "UTF-8"), handler)
                else:
                    sax.parseString(text, handler)
                return list(handler.datasources.keys())
            else:
                return []

    def componentsDataSources(self, names):
        """ provides a list of datasources from the given components

        :param names: given components
        :type names: :obj:`list` <:obj:`str`>
        :returns: list of datasource names from the given components
        :rtype: :obj:`list` <:obj:`str`>
        """
        mcnf = str(self.merge(names)).strip()
        if mcnf:
            cnf = self.__instantiate(mcnf)
            handler = ComponentHandler(self.__dsLabel)
            if sys.version_info > (3,):
                sax.parseString(bytes(cnf, "UTF-8"), handler)
            else:
                sax.parseString(cnf, handler)
            return list(handler.datasources.keys())
        else:
            return []

    def __findElements(self, text, label, delimiter=None, rechars=None):
        """ provides a list of elements from the given text

        :param text: give text
        :type text: :obj:`str`
        :param label: element label
        :type label: :obj:`str`
        :param delimiter: element end delimiter
        :param rechars: possible characters of element value
                      as a regular expression string
        :type rechars: :obj:`str`
        :returns: list of element names from the given text
        :rtype: :obj:`list` <:obj:`str`>
        """
        variables = []
        delimiter = delimiter or self.__delimiter
        rechars = rechars or r"[\w]+"
        index = text.find("$%s%s" % (label, delimiter))
        while index != -1:
            try:
                finder = re.finditer(
                    rechars, text[(index + len(label) + 2):]
                )
                if sys.version_info > (3,):
                    subc = finder.__next__().group(0)
                else:
                    subc = finder.next().group(0)
            except Exception:
                subc = ""
            name = subc.strip() if subc else ""
            if name:
                variables.append(name)
            index = text.find("$%s%s" % (label, delimiter), index + 1)

        return variables

    def componentVariables(self, name):
        """ provides a list of variables from the given components

        :param name: given component
        :type name: :obj:`str`
        :returns: list of variable names from the given components
        :rtype: :obj:`str`
        """
        cpl = []
        if self.__mydb:
            cpl = self.__mydb.components([name])
            if len(cpl) > 0:
                text = str(cpl[0]).strip()
                return list(self.__findElements(text, self.__varLabel))
            else:
                return []

    def componentsVariables(self, names):
        """ provides a tuple of variables from the given components

        :param names: given components
        :type names: :obj:`list` <:obj:`str`>

        :returns: tuple of variable names from the given components
        :rtype: :obj:`list` <:obj:`str`>
        """
        cnf = str(self.merge(names)).strip()
        if cnf:
            return list(self.__findElements(cnf, self.__varLabel))
        else:
            return []

    def dependentComponents(self, names, deps=None):
        """ provides dependent components

        :param names: component names to check
        :type names: :obj:`list` <:obj:`str`>
        :param deps: dictionery with dependent components
        :type deps: :obj:`dict` <:obj:`str`, :obj:`str`>
        :returns: list of depending components
        :rtype: :obj:`list` <:obj:`str`>
        """
        dps = deps if deps else {}
        for nm in names:
            if nm not in dps:
                dps[nm] = []
                cpl = self.__mydb.components([nm])
                if cpl:
                    dps[nm] = self.__findElements(cpl[0], self.__cpLabel)
                    self.dependentComponents(dps[nm], dps)
        return list(dps.keys())

    def dataSources(self, names, _=None):
        """ fetches the required datasources

        :param names: list of datasource names
        :type names: :obj:`list` <:obj:`str`>
        :returns: list of given datasources
        :rtype: :obj:`list` <:obj:`str`>
        """
        argout = []
        if self.__mydb:
            argout = self.__mydb.dataSources(names)
        return argout

    def availableComponents(self):
        """ fetches the names of available components

        :returns: list of available components
        :rtype: :obj:`list` <:obj:`str`>
        """
        argout = []
        if self.__mydb:
            argout = self.__mydb.availableComponents()
        return argout

    def availableSelections(self):
        """ fetches the names of available selections

        :returns: list of available selections
        :rtype: :obj:`list` <:obj:`str`>
        """
        argout = []
        if self.__mydb:
            argout = self.__mydb.availableSelections()
        return argout

    def availableDataSources(self):
        """ fetches the names of available datasources

        :returns: list of available datasources
        :rtype: :obj:`list` <:obj:`str`>
        """
        argout = []
        if self.__mydb:
            argout = self.__mydb.availableDataSources()
        return argout

    def storeComponent(self, name):
        """ stores the component from the xmlstring attribute

        :param name: name of the component to store
        :type name: :obj:`str`
        """
        if self.__mydb:
            try:
                if sys.version_info > (3,):
                    et.fromstring(
                        bytes(self.xmlstring, "UTF-8"),
                        parser=XMLParser(collect_ids=False))
                else:
                    et.fromstring(
                        self.xmlstring, parser=XMLParser(collect_ids=False))
            except Exception as e:
                raise WrongXMLError("WrongXMLError: %s" % str(e))
            self.__mydb.storeComponent(name, self.xmlstring)

    def storeSelection(self, name):
        """ stores the selection from the xmlstring attribute

        :param name: name of the selection to store
        :type name: :obj:`str`
        """
        if self.__mydb:
            try:
                json.loads(self.selection)
            except Exception as e:
                raise WrongJSONError("WrongJSONError: %s" % str(e))
            self.__mydb.storeSelection(name, self.selection)

    def storeDataSource(self, name):
        """ stores the datasource from the xmlstring attribute

        :param name: name of the datasource to store
        :type name: :obj:`str`
        """
        if self.__mydb:
            try:
                if sys.version_info > (3,):
                    et.fromstring(
                        bytes(self.xmlstring, "UTF-8"),
                        parser=XMLParser(collect_ids=False))
                else:
                    et.fromstring(
                        self.xmlstring, parser=XMLParser(collect_ids=False))
            except Exception as e:
                raise WrongXMLError("WrongXMLError: %s" % str(e))
            self.__mydb.storeDataSource(name, self.xmlstring)

    def deleteComponent(self, name):
        """ deletes the given component

        :param name: name of the component to delete
        :type name: :obj:`str`
        """
        if self.__mydb:
            self.__mydb.deleteComponent(name)

    def deleteSelection(self, name):
        """ deletes the given selection

        :param name: name of the selection to delete
        :type name: :obj:`str`
        """
        if self.__mydb:
            self.__mydb.deleteSelection(name)

    def deleteDataSource(self, name):
        """ deletes the given datasource

        :param name: name of the datasource to delete
        :type name: :obj:`str`
        """
        if self.__mydb:
            self.__mydb.deleteDataSource(name)

    def setComponentDataSources(self, jdict):
        """ sets component datasources according to given dict

        :param jdict: JSON dict of component datasources
        :type jdict: :obj:`str`
        """
        cps = json.loads(jdict)
        avcp = set(self.availableComponents())
        for cpname, dsdict in cps.items():
            if cpname.startswith(self.__templabel):
                tcpname = cpname
                cpname = cpname[len(self.__templabel):]
            else:
                tcpname = self.__templabel + cpname
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
            disds = set()
            for tds, ds in dsdict.items():
                if tds not in tcpdss:
                    raise NonregisteredDBRecordError(
                        "The datasource %s absent in the component %s"
                        % (tds, tcpname))
                elif ds:
                    self.__parameters[str(tds)] = "$datasources.%s" % ds
                else:
                    self.__parameters[str(tds)] = ""
                    disds.add(str(tds))
            if disds:
                tcomp = self.__commentDataSources(tcomp, disds)
            comp = self.__attachElements(
                tcomp, self.__dsLabel,
                list(self.__parameters.keys()),
                self.__getParameter, onlyexisting=True)
            self.__mydb.storeComponent(cpname, comp)

    @classmethod
    def __commentDataSources(cls, comp, disds):
        """ switch diable datasources into POSTRUN mode

        :param comp: xml component
        :type comp: :obj:`str`
        :param disds: list of disable datasources
        :type disds: :obj:`list` <:obj:`str`>
        """
        mgr = Merger()
        mgr.switchdatasources = list(disds) or []
        mgr.modesToSwitch = {
            "INIT": "POSTRUN",
            "FINAL": "POSTRUN",
            "STEP": "POSTRUN"}
        mgr.collect([comp])
        mgr.merge()
        return mgr.toString()

    def setMandatoryComponents(self, names):
        """ sets the mandtaory components

        :param names: list of component names
        :type names: :obj:`list` <:obj:`str`>
        """
        for name in names:
            self.__mydb.setMandatory(name)

    def unsetMandatoryComponents(self, names):
        """ sets the mandatory components

        :param names: list of component names
        :type names: :obj:`list` <:obj:`str`>
        """
        for name in names:
            self.__mydb.unsetMandatory(name)

    def mandatoryComponents(self):
        """ provides names of the mandatory components

        :returns: mandatory components
        :rtype: :obj:`list` <:obj:`str`>
        """
        argout = []
        if self.__mydb:
            argout = self.__mydb.mandatory()
        return argout

    def __getVariable(self, name, default=None):
        """ provides variable value

        :param name: variable name
        :type name: :obj:`str`
        """
        if len(name) > 0 and name[0] and name[0] in self.__parameters:
            return [self.__parameters[name[0]]]
        elif default is not None:
            return [str(default)]
        else:
            return [""]

    def __getParameter(self, name, _=None):
        """ provides parameter value

        :param name: parameter name
        :type name: :obj:`str`
        """
        if len(name) > 0 and name[0] and name[0] in self.__parameters:
            return [self.__parameters[name[0]]]
        else:
            return []

    def __attachElements(self, component, label, keys, funValue,
                         tag=None, onlyexisting=False):
        """ attaches elements to component

        :param component: given component
        :type component: :obj:`str`
        :param label: element label
        :type label: :obj:`str`
        :param keys: element names
        :type label: :obj:`list` <:obj:`str`>
        :param funValue: function of element value
        :type funValue: :obj:`instancemethod`
        :param tag: xml tag
        :type tag: :obj:`str`
        :param onlyexisting: attachElement only if exists
        :type onlyexisting: :obj:`bool`
        :returns: component with attached variables
        :rtype: :obj:`str`
        """
        index = component.find("$%s%s" % (label, self.__delimiter))
        while index != -1:
            defsubc = None
            subc = ''
            dsubc = ''
            try:
                finder = re.finditer(
                    r"[\w]+",
                    component[(index + len(label) + 2):])
                if sys.version_info > (3,):
                    subc = finder.__next__().group(0)
                else:
                    subc = finder.next().group(0)

                if not tag:
                    offset = index + len(subc) + len(label) + 2
                    if component[offset] == '#':
                        if component[offset + 1:offset + 7] == '&quot;':
                            soff = component[(offset + 7):].find('&quot;')
                            dsubc = component[
                                (offset + 1):(offset + 13 + soff)]
                            defsubc = dsubc[6:-6].replace('\\"', '"')
                        elif component[offset + 1:offset + 8] == '\\&quot;':
                            soff = component[(offset + 8):].find('\\&quot;')
                            dsubc = component[
                                (offset + 1):(offset + 15 + soff)]
                            defsubc = dsubc[7:-7].replace('\\"', '"')
                        else:
                            finder = re.finditer(
                                r"([\"'])(?:\\\1|.)*?\1",
                                component[(offset + 1):])
                            if sys.version_info > (3,):
                                dsubc = finder.__next__().group(0)
                            else:
                                dsubc = finder.next().group(0)
                            if dsubc:
                                if dsubc[0] == "'":
                                    defsubc = dsubc[1:-1].replace("\\'", "'")
                                elif dsubc[0] == '"':
                                    defsubc = dsubc[1:-1].replace('\\"', '"')
            except Exception:
                pass
            name = subc.strip() if subc else ""
            if name:
                if tag and name not in keys:
                    raise NonregisteredDBRecordError(
                        "The %s %s of %s not registered in the DataBase" % (
                            tag if tag else "variable", name, component))
                try:
                    xmlds = funValue([name], defsubc)
                except Exception:
                    xmlds = []
                if not onlyexisting and not xmlds:
                    raise NonregisteredDBRecordError(
                        "The %s %s of %s not registered" % (
                            tag if tag else "variable", name, component))
                if tag:
                    if sys.version_info > (3,):
                        root = et.fromstring(
                            bytes(xmlds[0], "UTF-8"),
                            parser=XMLParser(collect_ids=False))
                    else:
                        root = et.fromstring(
                            xmlds[0], parser=XMLParser(collect_ids=False))
                        # dom = parseString(xmlds[0])
                    if root.tag == tag:
                        etds = [root]
                    else:
                        etds = root.findall(".//%s" % tag)
                    # domds = dom.getElementsByTagName(tag)
                    if not etds:
                        raise NonregisteredDBRecordError(
                            "The %s %s of %s not registered in the DataBase"
                            % (tag if tag else "variable", name, component))
                    ds = _toxml(etds[0])
                    if not ds:
                        raise NonregisteredDBRecordError(
                            "The %s %s of %s not registered" % (
                                tag if tag else "variable", name, component))
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
                    "The %s %s of %s not registered" % (
                        tag if tag else "variable", name, component))
        return component

    def __attachVariables(self, component, cpvars=None):
        """ attaches variables to component

        :param component: given component
        :type component: :obj:`str`
        :param cpvars: dictionary with component variable values
        :type cpvars: :obj:`dict` <:obj:`str` , :obj:`str`>
        :returns: component with attached variables
        :rtype: :obj:`str`
        """
        if not component:
            return
        self.__parameters = {}
        js = json.loads(self.variables)
        targs = cpvars or {}
        targs.update(dict(js.items()))
        for k in targs.keys():
            self.__parameters[str(k)] = str(targs[k])
        return self.__attachElements(
            component, self.__varLabel,
            list(self.__parameters.keys()), self.__getVariable)

    def __attachComponents(self, component):
        """ attaches variables to component

        :param component: given component
        :type component: :obj:`str`
        :returns: component with attached variables
        :rtype: :obj:`str`
        """
        if not component:
            return
        return self.__attachElements(
            component, self.__cpLabel, [], lambda x, y: [""])

    def __attachDataSources(self, component):
        """ attaches datasources to component

        :param component: given component
        :type component: :obj:`str`
        :returns: component with attached datasources
        :rtype: :obj:`str`
        """
        if not component:
            return
        return self.__attachElements(
            component, self.__dsLabel,
            self.availableDataSources(), self.dataSources,
            "datasource")

    def merge(self, names):
        """ merges the give components

        :param names: list of component names
        :type names: :obj:`list` <:obj:`str`>
        :return: merged components
        :rtype: :obj:`str`
        """
        return self.__mergeVars(names, False)

    def __variableComponentValues(self, comps):
        """ finds variable values defined in components

        :param comps: list of component xml strings
        :type comps: :obj:`list` <:obj:`str`>
        :returns: dictionary with variable values
        :rtype: :obj:`dict` <:obj:`str` , :obj:`str`>
        """
        cpvars = {}
        for cp in comps:
            varls = self.__findElements(cp, self.__varLabel, "(", r"[=\w]+")
            for var in varls:
                if "=" in var:
                    key, value = var.split("=")
                cpvars[str(key)] = str(value)
        return cpvars

    def __mergeVars(self, names, withVariables=False):
        """ merges the give components

        :param names: list of component names
        :type names: :obj:`list` <:obj:`str`>
        :param withVariables: if true variables will be substituted
        :param withVariables: :obj:`bool`
        :returns: merged components
        :rtype: :obj:`str`
        """
        xml = ""
        if self.__mydb:
            allnames = self.dependentComponents(
                list(set(self.__mydb.mandatory() + names)))
            comps = self.__mydb.components(list(set(allnames)))
            if withVariables:
                cpvars = self.__variableComponentValues(comps)
                comps = [self.__attachVariables(cp, cpvars) for cp in comps]
            xml = self.__merge(comps)
        return xml if xml is not None else ""

    def __merge(self, xmls):
        """ merges the give component xmls

        :param xmls: list of component xmls
        :type xmls: :obj:`list` <:obj:`str`>
        :returns: merged components
        :rtype: :obj:`str`
        """
        mgr = Merger()
        mgr.switchdatasources = json.loads(self.stepdatasources)
        mgr.linkdatasources = json.loads(self.linkdatasources)
        mgr.canfaildatasources = json.loads(self.canfaildatasources)
        mgr.collect(xmls)
        mgr.merge()
        return mgr.toString()

    def createConfiguration(self, names):
        """ creates the final configuration string in the xmlstring attribute

        :param names: list of component names
        :type names: :obj:`list` <:obj:`str`>
        """
        cnf = self.__mergeVars(names, withVariables=True)
        cnf = self.__instantiate(cnf)
        cnfMerged = self.__merge([cnf])
        if cnfMerged and hasattr(cnfMerged, "strip") and cnfMerged.strip():
            if sys.version_info > (3,):
                reparsed = et.fromstring(
                    bytes(cnfMerged, "UTF-8"),
                    parser=XMLParser(collect_ids=False))
            else:
                reparsed = et.fromstring(
                    cnfMerged, parser=XMLParser(collect_ids=False))
            xmls = _tostr(etree.tostring(reparsed, encoding='utf8',
                                         method='xml', pretty_print=True))
            if xmls.startswith("<?xml"):
                self.xmlstring = xmls
            else:
                self.xmlstring = "<?xml version='1.0' encoding='utf8'?>" + xmls
        else:
            self.xmlstring = ''
        self._streams.info("XMLConfigurator::createConfiguration() "
                           "- Create configuration")


if __name__ == "__main__":

    try:
        #: (:class:`nxsconfigserver.XMLConfigurator.XMLConfigurator`)  \
        #:     configurer object
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
