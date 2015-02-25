#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2015 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
## \package nxsconfigserver nexdatas
## \file ComponentParser.py
# Class for searching database names in components

""" Parser for searching database names in components """

from xml import sax

import sys
import os
import re


## SAX2 parser
class ComponentHandler(sax.ContentHandler):

    ## constructor
    # \brief It constructs parser and sets variables to default values
    def __init__(self, dsLabel="datasources", delimiter='.'):
        sax.ContentHandler.__init__(self)
        ##  dictionary with datasources
        self.datasources = {}
        ## tag name
        self.__tag = "datasource"
        ## delimiter
        self.__delimiter = delimiter
        ## unnamed datasource counter
        self.__counter = 0
        ## datasource label
        self.__dsLabel = dsLabel
        ## containing datasources
        self.__withDS = ["field", "attribute"]
        ## content flag
        self.__stack = []
        ## content
        self.__content = {}
        for tag in self.__withDS:
            self.__content[tag] = []

    ## adds the tag content
    # \param content partial content of the tag
    def characters(self, content):
        if self.__stack[-1] in self.__withDS:
            self.__content[self.__stack[-1]].append(content)

    ##  parses the opening tag
    # \param name tag name
    # \param attrs attribute dictionary
    def startElement(self, name, attrs):
        self.__stack.append(name)
        if self.__tag and name == self.__tag:
            if "name" in attrs.keys():
                aName = attrs["name"]
            else:
                aName = "__unnamed__%s" % self.__counter
                self.__counter += 1
            if "type" in attrs.keys():
                aType = attrs["type"]
            else:
                aType = ""
            self.datasources[aName] = aType

    ## parses the closing tag
    # \param name tag name
    def endElement(self, name):
        tag = self.__stack[-1]
        if tag in self.__withDS:
            text = "".join(self.__content[tag]).strip()
            index = text.find("$%s%s" % (
                    self.__dsLabel, self.__delimiter))
            while index != -1:
                try:
                    subc = re.finditer(
                        r"[\w]+",
                        text[(index + len(self.__dsLabel) + 2):]
                        ).next().group(0)
                except:
                    subc = ""
                aName = subc.strip() if subc else ""
                if aName:
                    self.datasources[aName] = "__FROM_DB__"
                index = text.find("$%s%s" % (
                        self.__dsLabel, self.__delimiter), index + 1)

            self.__content[tag] = []
        self.__stack.pop()


if __name__ == "__main__":

#

    ## second test xml
    www2 = """
<?xml version='1.0'?>
<definition type="" name="">
<group type="NXentry" name="entry1">
<group type="NXinstrument" name="instrument">
<group type="NXdetector" name="detector">
<field units="m" type="NX_FLOAT" name="counter1">
<strategy mode="STEP"/>
<datasource type="CLIENT">
<record name="exp_c01"/>
</datasource>
</field>
<field units="s" type="NX_FLOAT" name="counter2">
<strategy mode="STEP"/>
<datasource type="CLIENT">
<record name="exp_c02"/>
</datasource>
</field>
<field units="" type="NX_FLOAT" name="mca">
<dimensions rank="1">
<dim value="2048" index="1"/>
</dimensions>
<strategy mode="STEP"/>
<datasource type="TANGO">
<device member="attribute" name="p09/mca/exp.02"/>
<record name="Data"/>
</datasource>
</field>
</group>
</group>
<group type="NXdata" name="data">
<link target="/NXentry/NXinstrument/NXdetector/mca" name="data">
<doc>
          Link to mca in /NXentry/NXinstrument/NXdetector
        </doc>
</link>
<link target="/NXentry/NXinstrument/NXdetector/counter1" name="counter1">
<doc>
          Link to counter1 in /NXentry/NXinstrument/NXdetector
        </doc>
</link>
<link target="/NXentry/NXinstrument/NXdetector/counter2" name="counter2">
<doc>
          Link to counter2 in /NXentry/NXinstrument/NXdetector
        </doc>
</link>
</group>
</group>
<doc>definition</doc>
</definition>
"""
    ## first test XML
    www = """
<?xml version='1.0'?>
<definition type="" name="">
<group type="NXentry" name="entry1">
<group type="NXinstrument" name="instrument">
<group type="NXdetector" name="detector">
<field units="m" type="NX_FLOAT" name="counter1">
<strategy mode="STEP"/>
<datasource type="CLIENT">
<record name="exp_c01"/>
</datasource>
</field>
<field units="s" type="NX_FLOAT" name="counter2">
<strategy mode="STEP"/>
<datasource type="CLIENT">
<record name="exp_c02"/>
</datasource>
</field>
<field units="" type="NX_FLOAT" name="mca">
<dimensions rank="1">
<dim value="2048" index="1"/>
</dimensions>
<strategy mode="STEP"/>
<datasource type="TANGO">
<device member="attribute" name="p09/mca/exp.02"/>
<record name="Data"/>
</datasource>
</field>
</group>
</group>
<group type="NXdata" name="data">
<link target="/NXentry/NXinstrument/NXdetector/mca" name="data">
<doc>
          Link to mca in /NXentry/NXinstrument/NXdetector
        </doc>
</link>
<link target="/NXentry/NXinstrument/NXdetector/counter1" name="counter1">
<doc>
          Link to counter1 in /NXentry/NXinstrument/NXdetector
        </doc>
</link>
<link target="/NXentry/NXinstrument/NXdetector/counter2" name="counter2">
<doc>
          Link to counter2 in /NXentry/NXinstrument/NXdetector
        </doc>
</link>
</group>
</group>
<doc>definition</doc>
</definition>
"""

    if len(sys.argv) < 2:
        print "usage: ComponentParser.py  <XMLinput>"
    else:
        ## input XML file
        fi = sys.argv[1]
        if os.path.exists(fi):

            ## a parser object
            parser = sax.make_parser()

            ## a SAX2 handler object
            handler = ComponentHandler()
            parser.setContentHandler(handler)
            parser.parse(open(fi))
            print(handler.datasources)

            ## a SAX2 handler object
            handler = ComponentHandler()
            sax.parseString(str(www2).strip(), handler)
            print(handler.datasources)
