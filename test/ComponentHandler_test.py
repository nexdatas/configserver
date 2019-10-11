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
# \package test nexdatas.configserver
# \file ComponentHandlerTest.py
# unittests for Component Handler
#
import unittest
import sys
import struct

from xml import sax

from nxsconfigserver.ComponentParser import ComponentHandler


def parseEncode(text, element):
    if hasattr(text, "encode"):
        return sax.parseString(text.encode("utf8"), element)
    else:
        return text


# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture
class ComponentHandlerTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

    # Exception tester
    # \param exception expected exception
    # \param method called method
    # \param args list with method arguments
    # \param kwargs dictionary with method arguments
    def myAssertRaise(self, exception, method, *args, **kwargs):
        try:
            error = False
            method(*args, **kwargs)
        except Exception:
            error = True
        self.assertEqual(error, True)

    # test starter
    # \brief Common set up
    def setUp(self):
        print("\nsetting up...")

    # test closer
    # \brief Common tear down
    def tearDown(self):
        print("tearing down ...")

    # constructor test
    # \brief It tests default settings
    def test_constructor(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = ComponentHandler()
        self.assertEqual(el.datasources, {})

    # constructor test
    # \brief It tests default settings
    def test_constructor_param(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = ComponentHandler("myds")
        self.assertEqual(el.datasources, {})

    # tests start element method
    # \brief It tests default settings
    def test_startElement(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = ComponentHandler()
        self.assertEqual(el.datasources, {})
        name = "datasource2"
        attr = {"name": "mydt"}
        self.assertEqual(el.startElement(name, attr), None)
        self.assertEqual(el.datasources, {})

        name = "datasource"
        attr = {"name2": "mydt"}
        self.assertEqual(el.startElement(name, attr), None)
        self.assertEqual(el.datasources, {'__unnamed__0': ''})

        name = "datasource"
        attr = {"name": "myds"}
        self.assertEqual(el.startElement(name, attr), None)
        self.assertEqual(el.datasources, {'__unnamed__0': '', 'myds': ''})

        name = "datasource"
        attr = {"name": "myds2", "type": "TANGO"}
        self.assertEqual(el.startElement(name, attr), None)
        self.assertEqual(
            el.datasources,
            {'__unnamed__0': '', 'myds2': 'TANGO', 'myds': ''})

        name = "datasource"
        attr = {"type": "CLIENT"}
        self.assertEqual(el.startElement(name, attr), None)
        self.assertEqual(el.datasources,
                         {'__unnamed__0': '', '__unnamed__1': 'CLIENT',
                          'myds2': 'TANGO', 'myds': ''})

    # tests start element method
    # \brief It tests default settings
    def test_startElement_2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = ComponentHandler()
        self.assertEqual(el.datasources, {})
        name = "datasource2"
        attr = {"name2": "mydt"}
        self.assertEqual(el.startElement(name, attr), None)
        self.assertEqual(el.datasources, {})

        name = "datasource"
        attr = {"name2": "mydt"}
        self.assertEqual(el.startElement(name, attr), None)
        self.assertEqual(el.datasources, {'__unnamed__0': ''})

        name = "datasource"
        attr = {"name": "myds", "name2": "mydt"}
        self.assertEqual(el.startElement(name, attr), None)
        self.assertEqual(el.datasources, {'__unnamed__0': '', 'myds': ''})

        name = "datasource"
        attr = {"name": "myds2", "type": "CLIENT", "name2": "mydt"}
        self.assertEqual(el.startElement(name, attr), None)
        self.assertEqual(
            el.datasources,
            {'__unnamed__0': '', 'myds2': 'CLIENT', 'myds': ''})

        name = "datasource"
        attr = {"type": "TANGO", "name2": "mydt", "name2": "mydt"}
        self.assertEqual(el.startElement(name, attr), None)
        self.assertEqual(el.datasources,
                         {'__unnamed__0': '', '__unnamed__1': 'TANGO',
                          'myds2': 'CLIENT', 'myds': ''})

    # tests start element method
    # \brief It tests default settings
    def test_startendElement_field(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = ComponentHandler()
        self.assertEqual(el.datasources, {})
        name = "field"
        attr = {"name2": "mydt"}
        ds = "extr_mot1"
        self.assertEqual(el.startElement(name, attr), None)
        self.assertEqual(el.characters("$datasources.%s" % ds), None)
        self.assertEqual(el.endElement(name), None)
        self.assertEqual(el.datasources, {'extr_mot1': '__FROM_DB__'})

    # tests start element method
    # \brief It tests default settings
    def test_startendElement_attribute(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = ComponentHandler()
        self.assertEqual(el.datasources, {})
        name = "attribute"
        attr = {"name2": "mydt"}
        ds = "extr_mot1"
        self.assertEqual(el.startElement(name, attr), None)
        self.assertEqual(el.characters("$datasources.%s" % ds), None)
        self.assertEqual(el.endElement(name), None)
        self.assertEqual(el.datasources, {'extr_mot1': '__FROM_DB__'})

    # tests start element method
    # \brief It tests default settings
    def test_startendElement_group(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = ComponentHandler()
        self.assertEqual(el.datasources, {})
        name = "group"
        attr = {"name2": "mydt"}
        ds = "extr_mot1"
        self.assertEqual(el.startElement(name, attr), None)
        self.assertEqual(el.characters("$datasources.%s" % ds), None)
        self.assertEqual(el.endElement(name), None)
        self.assertEqual(el.datasources, {})

    # tests start element method
    # \brief It tests default settings
    def test_startendElement_fields(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = ComponentHandler()
        self.assertEqual(el.datasources, {})
        name = "field"
        attr = {"name2": "mydt"}
        ds = "extr_mot1"
        ds2 = "extr_mot2"
        self.assertEqual(el.startElement(name, attr), None)
        self.assertEqual(el.characters("$datasources.%s" % ds), None)
        self.assertEqual(el.endElement(name), None)
        self.assertEqual(el.startElement(name, attr), None)
        self.assertEqual(el.characters("$datasources.%s" % ds2), None)
        self.assertEqual(el.endElement(name), None)
        self.assertEqual(
            el.datasources,
            {'extr_mot1': '__FROM_DB__', 'extr_mot2': '__FROM_DB__'})

    # tests start element method
    # \brief It tests default settings
    def test_startendElement_fields_2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = ComponentHandler()
        self.assertEqual(el.datasources, {})
        name = "field"
        attr = {"name2": "mydt"}
        ds = "extr_mot1"
        ds2 = "extr_mot2"
        self.assertEqual(el.startElement(name, attr), None)
        self.assertEqual(el.characters("$datasources.%s" % ds), None)
        self.assertEqual(el.endElement(name), None)
        self.assertEqual(el.startElement(name, attr), None)
        self.assertEqual(el.characters("datasources.%s" % ds2), None)
        self.assertEqual(el.endElement(name), None)
        self.assertEqual(el.datasources, {'extr_mot1': '__FROM_DB__'})

    # tests start element method
    # \brief It tests default settings
    def test_startendElement_fieldattribute(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = ComponentHandler()
        self.assertEqual(el.datasources, {})
        name = "field"
        aname = "attribute"
        attr = {"name2": "mydt"}
        ds = "extr_mot1"
        ds2 = "extr_mot2"
        self.assertEqual(el.startElement(name, attr), None)
        self.assertEqual(el.startElement(aname, attr), None)
        self.assertEqual(el.characters("$datasources.%s" % ds2), None)
        self.assertEqual(el.endElement(name), None)
        self.assertEqual(el.characters("$datasources.%s" % ds), None)
        self.assertEqual(el.endElement(name), None)
        self.assertEqual(
            el.datasources,
            {'extr_mot1': '__FROM_DB__', 'extr_mot2': '__FROM_DB__'})

    # tests start element method
    # \brief It tests default settings
    def test_startendElement_fieldattribute2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = ComponentHandler()
        self.assertEqual(el.datasources, {})
        name = "field"
        aname = "attribute"
        attr = {"name2": "mydt"}
        ds = "extr_mot1"
        ds2 = "extr_mot2"
        self.assertEqual(el.startElement(name, attr), None)
        self.assertEqual(el.characters("$datasources.%s" % ds), None)
        self.assertEqual(el.startElement(aname, attr), None)
        self.assertEqual(el.characters("$datasources.%s" % ds2), None)
        self.assertEqual(el.endElement(name), None)
        self.assertEqual(el.endElement(name), None)
        self.assertEqual(
            el.datasources,
            {'extr_mot1': '__FROM_DB__', 'extr_mot2': '__FROM_DB__'})

    # tests start element method
    # \brief It tests default settings
    def test_startendElement_fieldattributestrategy(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = ComponentHandler()
        self.assertEqual(el.datasources, {})
        name = "field"
        aname = "attribute"
        attr = {"name2": "mydt"}
        ds = "extr_mot1"
        ds2 = "extr_mot2"
        self.assertEqual(el.startElement(name, attr), None)
        self.assertEqual(el.characters("$datasources.%s" % ds), None)
        self.assertEqual(el.startElement(aname, attr), None)
        self.assertEqual(el.characters("$datasources.%s" % ds2), None)
        self.assertEqual(el.endElement(name), None)
        self.assertEqual(el.startElement("strategy", attr), None)
        self.assertEqual(el.endElement("strategy"), None)
        self.assertEqual(el.endElement(name), None)
        self.assertEqual(
            el.datasources,
            {'extr_mot1': '__FROM_DB__', 'extr_mot2': '__FROM_DB__'})

    # tests start element method
    # \brief It tests default settings
    def test_startendElement_groupfieldattributestrategy(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = ComponentHandler()
        self.assertEqual(el.datasources, {})
        name = "field"
        aname = "attribute"
        attr = {"name2": "mydt"}
        ds = "extr_mot1"
        ds2 = "extr_mot2"
        self.assertEqual(el.startElement("group", attr), None)
        self.assertEqual(el.startElement(name, attr), None)
        self.assertEqual(el.characters("$datasources.%s" % ds), None)
        self.assertEqual(el.startElement(aname, attr), None)
        self.assertEqual(el.characters("$datasources.%s" % ds2), None)
        self.assertEqual(el.endElement(name), None)
        self.assertEqual(el.startElement("strategy", attr), None)
        self.assertEqual(el.characters("$datasources.my"), None)
        self.assertEqual(el.endElement("strategy"), None)
        self.assertEqual(el.endElement(name), None)
        self.assertEqual(
            el.datasources,
            {'extr_mot1': '__FROM_DB__', 'extr_mot2': '__FROM_DB__'})
        self.assertEqual(el.endElement("group"), None)

    # constructor test
    # \brief It tests default settings
    def test_XML_empty(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = ComponentHandler()
        parseEncode(
            '<group name="mygroup" ><attribute name="type">NXentry'
            '</attribute></group>',
            el)
        self.assertEqual(el.datasources, {})

    # constructor test
    # \brief It tests default settings
    def test_XML_datasource(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = ComponentHandler()
        parseEncode(
            '<field name="myfield" ><datasource name2="TANGO">NXentry'
            '</datasource></field>',
            el)

        self.assertEqual(el.datasources, {u'__unnamed__0': ''})

    # constructor test
    # \brief It tests default settings
    def test_XML_datasource_empty(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = ComponentHandler()
        parseEncode('<field name="myfield" >$datasources.</field>', el)

        self.assertEqual(el.datasources, {})

    # constructor test
    # \brief It tests default settings
    def test_XML_datasource_name(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = ComponentHandler()
        parseEncode(
            '<field name="myfield" ><datasource name="myTANGO">NXentry'
            '</datasource></field>', el)
        self.assertEqual(el.datasources, {u'myTANGO': ''})

    # constructor test
    # \brief It tests default settings
    def test_XML_datasource_name_ext(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = ComponentHandler()
        parseEncode(
            '<field name="myfield" >$datasources.myTANGO</field>', el)

        self.assertEqual(el.datasources, {u'myTANGO': '__FROM_DB__'})

    # constructor test
    # \brief It tests default settings
    def test_XML_datasource_name_two_fields(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = ComponentHandler()
        parseEncode(
            '<group><field name="myfield" >$datasources.myTANGO</field>' +
            '<field name="myfield2" >$datasources.myTANGO2</field></group>',
            el)

        self.assertEqual(
            el.datasources,
            {u'myTANGO2': '__FROM_DB__', u'myTANGO': '__FROM_DB__'})

    # constructor test
    # \brief It tests default settings
    def test_XML_datasource_name_two_fields_group(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = ComponentHandler()
        parseEncode(
            '<group>$datasources.myTANGO<field name="myfield" >'
            '$datasources.myTANGO</field>'
            '<field name="myfield2" >$datasources.myTANGO2</field></group>',
            el)

        self.assertEqual(
            el.datasources,
            {u'myTANGO2': '__FROM_DB__', u'myTANGO': '__FROM_DB__'})

    # constructor test
    # \brief It tests default settings
    def test_XML_datasource_name_two_fields_withtags(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = ComponentHandler()
        parseEncode(
            '<group><field name="myfield" >$datasources.myTANGO<strategy/>'
            '</field><field name="myfield2" >$datasources.myTANGO2<doc/>'
            '</field></group>', el)

        self.assertEqual(
            el.datasources,
            {u'myTANGO2': '__FROM_DB__', u'myTANGO': '__FROM_DB__'})

    # constructor test
    # \brief It tests default settings
    def test_XML_datasource_name_attr_field(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = ComponentHandler()
        parseEncode(
            '<group><field name="myfield" >$datasources.myTANGO'
            '<attribute name="myattr" >$datasources.myTANGO2</attribute>'
            '</field></group>', el)

        self.assertEqual(
            el.datasources,
            {u'myTANGO2': '__FROM_DB__', u'myTANGO': '__FROM_DB__'})

    # constructor test
    # \brief It tests default settings
    def test_XML_datasource_name_attr_field_no(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = ComponentHandler("ds")
        parseEncode(
            '<group><field name="myfield" >$datasources.myTANGO'
            '<attribute name="myattr" >$datasources.myTANGO2</attribute>'
            '</field></group>', el)

        self.assertEqual(el.datasources, {})

    # constructor test
    # \brief It tests default settings
    def test_XML_datasource_name_attr_field_ds(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = ComponentHandler("ds")
        parseEncode(
            '<group><field name="myfield" >$ds.myTANGO'
            '<attribute name="myattr" >$ds.myTANGO2</attribute></field>'
            '</group>', el)

        self.assertEqual(
            el.datasources,
            {u'myTANGO2': '__FROM_DB__', u'myTANGO': '__FROM_DB__'})

    # constructor test
    # \brief It tests default settings
    def test_XML_datasource_type(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = ComponentHandler()
        parseEncode(
            '<field name="myfield" ><datasource type="TANGO">NXentry'
            '</datasource></field>', el)

        self.assertEqual(el.datasources, {'__unnamed__0': u'TANGO'})

    # constructor test
    # \brief It tests default settings
    def test_XML_datasource_type_name(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = ComponentHandler()
        parseEncode(
            '<field name="myfield" ><datasource type="TANGO" name="myTango">'
            'NXentry</datasource></field>', el)

        self.assertEqual(el.datasources, {u'myTango': u'TANGO'})

    # constructor test
    # \brief It tests default settings
    def test_XML_datasource_type_name_nxml(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = ComponentHandler()

    # first test XML
        nxml = """
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
<datasource name="counter" type="CLIENT">
<record name="exp_c02"/>
</datasource>
</field>
<field units="" type="NX_FLOAT" name="mca">
<dimensions rank="1">
<dim value="2048" index="1"/>
</dimensions>
<strategy mode="STEP"/>
<datasource name="counter2" type="TANGO">
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

        parseEncode(str(nxml).strip(), el)

        self.assertEqual(
            el.datasources,
            {'__unnamed__0': u'CLIENT', u'counter': u'CLIENT',
             u'counter2': u'TANGO'})


if __name__ == '__main__':
    unittest.main()
