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
## \package test nexdatas.configserver
## \file MergerTest.py
# unittests for Merger
#
import unittest
import os
import sys
import struct

from xml import sax

from mcs.Merger import Merger, UndefinedTagError, IncompatibleNodeError


## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


## test fixture
class MergerTest(unittest.TestCase):

    ## constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)




        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

    ## Exception tester
    # \param exception expected exception
    # \param method called method      
    # \param args list with method arguments
    # \param kwargs dictionary with method arguments
    def myAssertRaise(self, exception, method, *args, **kwargs):
        try:
            error =  False
            method(*args, **kwargs)
        except exception, e:
            error = True
        self.assertEqual(error, True)



    ## test starter
    # \brief Common set up
    def setUp(self):
        print "\nsetting up..."        

    ## test closer
    # \brief Common tear down
    def tearDown(self):
        print "tearing down ..."

    ## constructor test
    # \brief It tests default settings
    def test_constructor(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        self.assertEqual(el.singles, ['datasource', 'strategy', 'dimensions', 'definition', 'record', 'device', 'query', 'database', 'door'])
        self.assertEqual(el.children, {'definition': ('group', 'field', 'attribute', 'link', 'component', 'doc', 'symbols'), 'group': ('group', 'field', 'attribute', 'link', 'component', 'doc'), 'dimensions': ('dim', 'doc'), 'attribute': ('datasource', 'strategy', 'enumeration', 'doc'), 'field': ('attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'), 'link': 'doc', 'datasource': ('record', 'doc', 'device', 'database', 'query', 'door')})
        self.assertEqual(el.uniqueText, ['field','attribute','query','strategy'])
        self.assertEqual(el.toString(), None)


    ## test collect
    # \brief It tests default settings
    def test_collect_default(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        self.assertEqual(el.collect([]), None)
        self.assertEqual(el.toString(), None)

    ## test collect
    # \brief It tests default settings
    def test_collect_default_2(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        self.assertEqual(el.collect(["<definition/>"]), None)
        self.assertEqual(el.toString(), '<?xml version="1.0" ?>\n<definition/>')

    ## test collect
    # \brief It tests default settings
    def test_collect_def_group(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        self.myAssertRaise(UndefinedTagError, el.collect, ["<group type='NXentry'/>"])
    



    ## test collect
    # \brief It tests default settings
    def test_collect_group(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        self.assertEqual(el.collect(["<definition/>","<definition><group type='NXentry'/></definition>"]), None)
        self.assertEqual(el.toString(), '<?xml version="1.0" ?>\n<definition> <group type="NXentry"/></definition>')


    ## test collect
    # \brief It tests default settings
    def test_collect_group_5(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        self.assertEqual(el.collect(["<definition><group type='NXentry'/></definition>"]*5), None)
        self.assertEqual(el.toString(), '<?xml version="1.0" ?>\n<definition> <group type="NXentry"/> <group type="NXentry"/> <group type="NXentry"/> <group type="NXentry"/> <group type="NXentry"/></definition>')


    ## test collect
    # \brief It tests default settings
    def test_collect_group_group(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        self.assertEqual(el.collect(["<definition><group type='NXentry'/></definition>","<definition><group type='NXentry2'/></definition>"]), None)
        self.assertEqual(el.toString(), '<?xml version="1.0" ?>\n<definition> <group type="NXentry"/> <group type="NXentry2"/></definition>')


    ## test collect
    # \brief It tests default settings
    def test_collect_group_group_error(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        self.myAssertRaise(UndefinedTagError, el.collect, ["<definition><group type='NXentry'/></definition>","<group/>"])


    ## test collect
    # \brief It tests default settings
    def test_collect_group_group_error_2(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        self.myAssertRaise(UndefinedTagError, el.collect, ["<group/>","<definition><group type='NXentry'/></definition>"])

   ## test collect
    # \brief It tests default settings
    def test_collect_group_field_3(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        self.assertEqual(el.collect(["<definition><group type='NXentry'><field type='field'/></group></definition>"]*3), None)
        self.assertEqual(el.toString(), '<?xml version="1.0" ?>\n<definition> <group type="NXentry">  <field type="field"/> </group> <group type="NXentry">  <field type="field"/> </group> <group type="NXentry">  <field type="field"/> </group></definition>')


   ## test collect
    # \brief It tests default settings
    def test_collect_group_group_field(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        self.assertEqual(el.collect(["<definition><group type='NXentry'><field name='field1'/></group></definition>","<definition><group type='NXentry2'/><field name='field1'/></definition>"]), None)
        self.assertEqual(el.toString(), '<?xml version="1.0" ?>\n<definition> <group type="NXentry">  <field name="field1"/> </group> <group type="NXentry2"/> <field name="field1"/></definition>')




    ## test collect
    # \brief It tests default settings
    def test_merge_default(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
#        self.assertEqual(el.collect([]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(el.toString(), None)


    ## test collect
    # \brief It tests default settings
    def test_merge_default_2(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        self.assertEqual(el.collect([]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(el.toString(), None)

    ## test collect
    # \brief It tests default settings
    def test_merge_definition(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        self.assertEqual(el.collect(["<definition/>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(el.toString(), '<?xml version="1.0" ?>\n<definition/>')


    ## test collect
    # \brief It tests default settings
    def test_merge_group(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        self.assertEqual(el.collect(["<definition/>","<definition><group type='NXentry'/></definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(el.toString(), '<?xml version="1.0" ?>\n<definition> <group type="NXentry"/></definition>')


    ## test collect
    # \brief It tests default settings
    def test_merge_group_5(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        self.assertEqual(el.collect(["<definition><group type='NXentry'/></definition>"]*5), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(el.toString(), '<?xml version="1.0" ?>\n<definition> <group type="NXentry"/></definition>')



    ## test collect
    # \brief It tests default settings
    def test_merge_group_group(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        self.assertEqual(el.collect(["<definition><group type='NXentry'/></definition>","<definition><group type='NXentry2'/></definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(el.toString(), '<?xml version="1.0" ?>\n<definition> <group type="NXentry"/> <group type="NXentry2"/></definition>')


    ## test collect
    # \brief It tests default settings
    def test_merge_group_group_2(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        self.assertEqual(el.collect(["<definition><group name='entry'/></definition>","<definition><group type='NXentry2'/></definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(el.toString(), '<?xml version="1.0" ?>\n<definition> <group name="entry"/> <group type="NXentry2"/></definition>')


    ## test collect
    # \brief It tests default settings
    def test_merge_group_group_3(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        self.assertEqual(el.collect(["<definition><group name='entry'/></definition>","<definition><group name='entry' type='NXentry'/></definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(el.toString(), '<?xml version="1.0" ?>\n<definition> <group name="entry" type="NXentry"/></definition>')


    ## test collect
    # \brief It tests default settings
    def test_merge_group_group_4(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        self.assertEqual(el.collect(["<definition><group name='entry2'/></definition>","<definition><group name='entry' type='NXentry'/></definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(el.toString(), '<?xml version="1.0" ?>\n<definition> <group name="entry2"/> <group name="entry" type="NXentry"/></definition>')



    ## test collect
    # \brief It tests default settings
    def test_merge_group_field_3(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        self.assertEqual(el.collect(["<definition><group type='NXentry'><field type='field'/></group></definition>"]*3), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(el.toString(), '<?xml version="1.0" ?>\n<definition> <group type="NXentry">  <field type="field"/> </group></definition>')


 
    ## test collect
    # \brief It tests default settings
    def test_merge_group_field_4(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        self.assertEqual(el.collect(["<definition><group type='NXentry'><field type='field'/></group></definition>"]*10), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(el.toString(), '<?xml version="1.0" ?>\n<definition> <group type="NXentry">  <field type="field"/> </group></definition>')


    ## test collect
    # \brief It tests default settings
    def test_merge_group_field_5(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        self.assertEqual(el.collect(["<definition><group  name='entry' type='NXentry'><field type='field'/></group></definition>","<definition><group name='entry' type='NXentry'><field type='field'/></group></definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(el.toString(), '<?xml version="1.0" ?>\n<definition> <group name="entry" type="NXentry">  <field type="field"/> </group></definition>')


    ## test collect
    # \brief It tests default settings
    def test_merge_group_field_name_error(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        self.assertEqual(el.collect(["<definition><group  name='entry' type='NXentry'><field type='field'/></group></definition>","<definition><group name='entry' type='NXentry2'><field type='field'/></group></definition>"]), None)
        self.myAssertRaise(IncompatibleNodeError,el.merge)



    ## test collect
    # \brief It tests default settings
    def test_merge_single_name(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        el.singles = []
        self.assertEqual(el.collect(["<definition><group  name='entry' type='NXentry'><field type='field'/></group></definition>","<definition><group name='entry2' type='NXentry2'><field type='field'/></group></definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(el.toString(),'<?xml version="1.0" ?>\n<definition> <group name="entry" type="NXentry">  <field type="field"/> </group> <group name="entry2" type="NXentry2">  <field type="field"/> </group></definition>')


    ## test collect
    # \brief It tests default settings
    def test_merge_single_name_error(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        el.singles = ['group']
        self.assertEqual(el.collect(["<definition><group  name='entry' type='NXentry'><field type='field'/></group></definition>","<definition><group name='entry2' type='NXentry2'><field type='field'/></group></definition>"]), None)
        self.myAssertRaise(IncompatibleNodeError,el.merge)



    ## test collect
    # \brief It tests default settings
    def test_merge_single(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        el.singles = ['field']
        self.assertEqual(el.collect(["<definition><group  type='NXentry'><field type='field'/></group></definition>","<definition><group type='NXentry2'><field type='field'/></group></definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(el.toString(),'<?xml version="1.0" ?>\n<definition> <group type="NXentry">  <field type="field"/> </group> <group type="NXentry2">  <field type="field"/> </group></definition>')


    ## test collect
    # \brief It tests default settings
    def test_merge_single_error(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        el.singles = ['group']
        self.assertEqual(el.collect(["<definition><group type='NXentry'><field type='field'/></group></definition>","<definition><group  type='NXentry2'><field type='field'/></group></definition>"]), None)
        self.myAssertRaise(IncompatibleNodeError,el.merge)



    ## test collect
    # \brief It tests default settings
    def test_merge_uniqueText(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        el.uniqueText = []
        self.assertEqual(el.collect(["<definition><group  name='entry' type='NXentry'><field type='field'>My text </field></group></definition>","<definition><group  name='entry' type='NXentry'><field type='field'>My text 2 </field></group></definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(el.toString(),'<?xml version="1.0" ?>\n<definition> <group name="entry" type="NXentry">  <field type="field">   My text    My text 2   </field> </group></definition>')





    ## test collect
    # \brief It tests default settings
    def test_merge_uniqueText_error(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        el.uniqueText = ['field']
        self.assertEqual(el.collect(["<definition><group  name='entry' type='NXentry'><field type='field'>My text </field></group></definition>","<definition><group  name='entry' type='NXentry'><field type='field'>My text 2 </field></group></definition>"]), None)
        self.myAssertRaise(IncompatibleNodeError,el.merge)


    ## test collect
    # \brief It tests default settings
    def test_merge_uniqueText_error_2(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        el.uniqueText = ['datasource','field']
        self.assertEqual(el.collect(["<definition><group  name='entry' type='NXentry'><field type='field'>My text </field></group></definition>","<definition><group  name='entry' type='NXentry'><field type='field'>My text 2 </field></group></definition>"]), None)
        self.myAssertRaise(IncompatibleNodeError,el.merge)



    ## test collect
    # \brief It tests default settings
    def test_merge_children(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        el.children ={
            "datasource":("record", "doc", "device", "database", "query", "door"),
            "attribute":("datasource", "strategy", "enumeration", "doc"),
            "definition":("group", "field", "attribute", "link", "component", "doc", "symbols"),
            "dimensions":("dim", "doc"),
            "field":("attribute", "datasource", "doc", "dimensions", "enumeration", "strategy"),
            "group":("field", "group", "attribute", "link", "component", "doc"),
            "link":("doc")
            }
        self.assertEqual(el.collect(["<definition><group  name='entry' type='NXentry'><field type='field'/></group></definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(el.toString(),'<?xml version="1.0" ?>\n<definition> <group name="entry" type="NXentry">  <field type="field"/> </group></definition>')


    ## test collect
    # \brief It tests default settings
    def test_merge_children_error(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        el.children ={
            "datasource":("record", "doc", "device", "database", "query", "door"),
            "attribute":("datasource", "strategy", "enumeration", "doc"),
            "definition":("group", "field", "attribute", "link", "component", "doc", "symbols"),
            "dimensions":("dim", "doc"),
            "field":("attribute", "datasource", "doc", "dimensions", "enumeration", "strategy"),
            "group":("group", "attribute", "link", "component", "doc"),
            "link":("doc")
            }

        self.assertEqual(el.collect(["<definition><group  name='entry' type='NXentry'><field type='field'/></group></definition>"]), None)
        self.myAssertRaise(IncompatibleNodeError,el.merge)


    ## test collect
    # \brief It tests default settings
    def test_merge_children_2(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        el.children ={
            "datasource":("record", "doc", "device", "database", "query", "door"),
            "attribute":("datasource", "strategy", "enumeration", "doc"),
            "definition":("group", "field", "attribute", "link", "component", "doc", "symbols"),
            "dimensions":("dim", "doc"),
            "field":("attribute", "datasource", "doc", "dimensions", "enumeration", "strategy"),
            "group":("field", "group", "attribute", "link", "component", "doc"),
            "link":("doc")
            }
        self.assertEqual(el.collect(["<definition><group  name='entry' type='NXentry'><field type='field'/></group></definition>","<definition><group  name='entry' type='NXentry'><field /></group></definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(el.toString(),'<?xml version="1.0" ?>\n<definition> <group name="entry" type="NXentry">  <field type="field"/> </group></definition>')



    ## test collect
    # \brief It tests default settings
    def test_merge_children_error_2(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        el = Merger()
        el.children ={
            "datasource":("record", "doc", "device", "database", "query", "door"),
            "attribute":("datasource", "strategy", "enumeration", "doc"),
            "definition":("group", "field", "attribute", "link", "component", "doc", "symbols"),
            "dimensions":("dim", "doc"),
            "field":("attribute", "datasource", "doc", "dimensions", "enumeration", "strategy"),
            "group":("group", "attribute", "link", "component", "doc"),
            "link":("doc")
            }

        self.assertEqual(el.collect(["<definition><group name='entry' type='NXentry'><field type='field'/></group></definition>","<definition><group  name='entry' type='NXentry'><field /></group></definition>"]), None)
        self.myAssertRaise(IncompatibleNodeError,el.merge)

if __name__ == '__main__':
    unittest.main()
