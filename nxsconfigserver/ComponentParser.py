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

""" Parser for searching database names in components """

from xml import sax

import sys
import os
import re


class ComponentHandler(sax.ContentHandler):

    """ SAX2 parser
    """

    def __init__(self, dsLabel="datasources", delimiter='.'):
        """ constructor

        :param dsLabel: variable element label, e.g. 'datasources'
        :type dsLabel: :obj:`str`
        :param delimiter: variable element delimiter, e.g. '.'
        :type delimiter: :obj:`str`
        :brief: It constructs parser and sets variables to default values
        """
        sax.ContentHandler.__init__(self)
        #: (:obj:`dict` <:obj:`str` , :obj:`str`> ) dictionary with datasources
        self.datasources = {}
        #: (:obj:`str`) tag name
        self.__tag = "datasource"
        #: (:obj:`str`) delimiter
        self.__delimiter = delimiter
        #: (:obj:`int`) unnamed datasource counter
        self.__counter = 0
        #: (:obj:`str`) datasource label
        self.__dsLabel = dsLabel
        #: (:obj:`list` <:obj:`str`>) containing datasources
        self.__withDS = ["field", "attribute"]
        #: (:obj:`list` <:obj:`str`>) content flag
        self.__stack = []
        #: (:obj:`dict` <:obj:`str` , `list` <:obj:`str`>> ) content
        self.__content = {}
        for tag in self.__withDS:
            self.__content[tag] = []

    def characters(self, content):
        """ adds the tag content

        param content: partial content of the tag
        :type content: :obj:`str`
        """
        if self.__stack[-1] in self.__withDS:
            self.__content[self.__stack[-1]].append(content)

    def startElement(self, name, attrs):
        """ parses the opening tag

        :param name: tag name
        :type name: :obj:`str`
        :param attrs: attribute dictionary
        :type attrs: :obj:`dict` <:obj:`str`, :obj:`str`>
        """
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

    def endElement(self, name):
        """ parses the closing tag

        :param name: tag name
        :type name: :obj:`str`
        """
        tag = self.__stack[-1]
        if tag in self.__withDS:
            text = "".join(self.__content[tag]).strip()
            index = text.find("$%s%s" % (
                self.__dsLabel, self.__delimiter))
            while index != -1:
                try:
                    finder = re.finditer(
                        r"[\w]+",
                        text[(index + len(self.__dsLabel) + 2):]
                    )
                    if sys.version_info > (3,):
                        subc = finder.__next__().group(0)
                    else:
                        subc = finder.next().group(0)
                except Exception:
                    subc = ""
                aName = subc.strip() if subc else ""
                if aName:
                    self.datasources[aName] = "__FROM_DB__"
                index = text.find("$%s%s" % (
                    self.__dsLabel, self.__delimiter), index + 1)

            self.__content[tag] = []
        self.__stack.pop()


if __name__ == "__main__":

    #: second test xml
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
    #: first test XML
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
        print("usage: ComponentParser.py  <XMLinput>")
    else:
        #: (:obj:`str`) input XML file
        fi = sys.argv[1]
        if os.path.exists(fi):

            #: (:class:`xml.sax.xmlreader.XMLReader`) parser object
            parser = sax.make_parser()

            #: (:class:`FetchNameHandler`) SAX2 handler object
            handler = ComponentHandler()
            parser.setContentHandler(handler)
            parser.parse(open(fi))
            print(handler.datasources)

            #: (:class:`FetchNameHandler`)  SAX2 handler object
            handler = ComponentHandler()
            sax.parseString(str(www2).strip(), handler)
            print(handler.datasources)
