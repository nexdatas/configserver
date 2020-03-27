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
# \file MergerTest.py
# unittests for Merger
#
import unittest
# import os
import sys
import struct

from nxsconfigserver.Merger import (
    Merger, UndefinedTagError, IncompatibleNodeError)
try:
    from .checks import checkxmls, checknxmls
except Exception:
    from checks import checkxmls, checknxmls


# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture
class MergerTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"
        self.maxDiff = None

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

        el = Merger()
        self.assertEqual(
            el.singles,
            ['strategy', 'dimensions', 'definition', 'record', 'device',
             'query', 'database'])
        self.assertEqual(
            el.children,
            {'definition': ('group', 'field', 'attribute', 'link', 'component',
                            'doc', 'symbols'),
             'group': ('group', 'field', 'attribute', 'link', 'component',
                       'doc'),
             'dim': ('datasource', 'strategy', 'doc'),
             'dimensions': ('dim', 'doc'),
             'attribute': ('datasource', 'strategy', 'enumeration', 'doc',
                           'dimensions'),
             'field': ('attribute', 'datasource', 'doc', 'dimensions',
                       'enumeration', 'strategy'),
             'link': ('datasource', 'strategy', 'doc')})
        self.assertEqual(
            el.uniqueText,
            ['field', 'attribute', 'query', 'strategy', 'result'])
        self.assertEqual(
            el.tocut, ['NXtransformations', 'NXcollection'])
        self.assertEqual(el.toString(), None)

    # test collect
    # \brief It tests default settings
    def test_collect_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        self.assertEqual(el.collect([]), None)
        self.assertEqual(el.toString(), None)

    # test collect
    # \brief It tests default settings
    def test_collect_default_2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        self.assertEqual(el.collect(["<definition/>"]), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            "<?xml version='1.0' encoding='utf8'?><definition />")

    # test collect
    # \brief It tests default settings
    def test_collect_def_group(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        self.myAssertRaise(
            UndefinedTagError, el.collect, ["<group type='NXentry'/>"])

    # test collect
    # \brief It tests default settings
    def test_collect_group(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        self.assertEqual(
            el.collect(["<definition/>",
                        "<definition><group type='NXentry'/></definition>"]),
            None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?>'
            '<definition><group type="NXentry" />'
            '</definition>')

    # test collect
    # \brief It tests default settings
    def test_collect_group_5(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        self.assertEqual(
            el.collect(
                ["<definition><group type='NXentry'/></definition>"] * 5),
            None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?>'
            '<definition>'
            '<group type="NXentry" />'
            '<group type="NXentry" />'
            '<group type="NXentry" />'
            '<group type="NXentry" />'
            '<group type="NXentry" />'
            '</definition>')

    # test collect
    # \brief It tests default settings
    def test_collect_group_group(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        self.assertEqual(
            el.collect(["<definition><group type='NXentry'/></definition>",
                        "<definition><group type='NXentry2'/></definition>"]),
            None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?>'
            '<definition><group type="NXentry" />'
            '<group type="NXentry2" /></definition>')

    # test collect
    # \brief It tests default settings
    def test_collect_group_group_error(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        self.myAssertRaise(
            UndefinedTagError, el.collect,
            ["<definition><group type='NXentry'/></definition>", "<group/>"])

    # test collect
    # \brief It tests default settings
    def test_collect_group_group_error_2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        self.myAssertRaise(
            UndefinedTagError, el.collect,
            ["<group/>", "<definition><group type='NXentry'/></definition>"])

    # test collect
    # \brief It tests default settings
    def test_collect_group_field_3(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        self.assertEqual(
            el.collect(
                ["<definition><group type='NXentry'><field type='field'/>"
                 "</group></definition>"] * 3), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?>'
            '<definition><group type="NXentry">'
            '<field type="field" /></group><group type="NXentry">'
            '<field type="field" /></group><group type="NXentry">'
            '<field type="field" /></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_collect_group_group_field(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        self.assertEqual(
            el.collect(
                ["<definition><group type='NXentry'><field name='field1'/>"
                 "</group></definition>",
                 "<definition><group type='NXentry2'/>"
                 "<field name='field1'/></definition>"]), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?>'
            '<definition><group type="NXentry">'
            '<field name="field1" /></group>'
            '<group type="NXentry2" />'
            '<field name="field1" /></definition>')

    # test collect
    # \brief It tests default settings
    def test_merge_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
#        self.assertEqual(el.collect([]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(el.toString(), None)

    # test collect
    # \brief It tests default settings
    def test_merge_default_2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        self.assertEqual(el.collect([]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(el.toString(), None)

    # test collect
    # \brief It tests default settings
    def test_merge_definition(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        self.assertEqual(el.collect(["<definition/>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition />')

    # test collect
    # \brief It tests default settings
    def test_merge_group(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        self.assertEqual(
            el.collect(
                ["<definition/>",
                 "<definition><group type='NXentry'/></definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?>'
            '<definition><group type="NXentry" />'
            '</definition>')

    # test collect
    # \brief It tests default settings
    def test_merge_group_tocut(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        self.assertTrue("NXcollection" in el.tocut)
        self.assertEqual(
            el.collect(
                ["<definition/>",
                 "<definition><group type='NXcollection'/></definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(el.toString().replace("?>\n<", "?><"),
                         '<?xml version=\'1.0\' encoding=\'utf8\'?>'
                         '<definition />')

    # test collect
    # \brief It tests default settings
    def test_merge_group_tocut2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.tocut = ["NXentry"]
        self.assertEqual(
            el.collect(
                ["<definition/>",
                 "<definition><group type='NXentry'/></definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(el.toString().replace("?>\n<", "?><"),
                         '<?xml version=\'1.0\' encoding=\'utf8\'?>'
                         '<definition />')

    # test collect
    # \brief It tests default settings
    def test_merge_group_tocut3(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.tocut = []
        self.assertEqual(
            el.collect(
                ["<definition/>",
                 "<definition><group type='NXentry'/></definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?>'
            '<definition><group type="NXentry" />'
            '</definition>')

    # test collect
    # \brief It tests default settings
    def test_merge_group_tocut4(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.tocut = ["NXentry"]
        self.assertEqual(
            el.collect(
                ["<definition/>",
                 "<definition><group type='NXentry'><group/></group>"
                 "</definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?>'
            '<definition><group type="NXentry">'
            '<group /></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_merge_group_tocut5(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.tocut = ["NXentry"]
        self.assertEqual(
            el.collect(
                ["<definition/>",
                 "<definition><group type='NXentry' name='entry'></group>"
                 "</definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(el.toString().replace("?>\n<", "?><"),
                         '<?xml version=\'1.0\' encoding=\'utf8\'?>'
                         '<definition />')

    # test collect
    # \brief It tests default settings
    def test_merge_group_tocut6(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.tocut = ["NXentry"]
        self.assertEqual(
            el.collect(
                ["<definition/>",
                 "<definition><group type='NXentry' name='entry2'></group>"
                 "</definition>"]), None)
        self.assertEqual(el.merge(), None)
        checkxmls(
            self,
            el.toString(),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry2" type="NXentry" /></definition>')

    # test collect
    # \brief It tests default settings
    def test_merge_group_tocut7(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.tocut = ["NXentry"]
        self.assertEqual(
            el.collect(
                ["<definition/>",
                 "<definition>"
                 "<group type='NXentry' name='entry' attr='ble ble'></group>"
                 "</definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(el.merge(), None)
        checkxmls(
            self,
            el.toString(),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group attr="ble ble" name="entry" type="NXentry" />'
            '</definition>')

    # test collect
    # \brief It tests default settings
    def test_merge_group_tocut8(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.tocut = ["NXentry", "NXtransformations"]
        self.assertEqual(
            el.collect(
                ["<definition/>",
                 "<definition><group type='NXentry' name='entry2'>"
                 "<group type='NXtransformations'/></group></definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        checkxmls(
            self,
            el.toString(),
            '<?xml version=\'1.0\' encoding=\'utf8\'?>'
            '<definition>'
            '<group name="entry2" type="NXentry" /></definition>')

    # test collect
    # \brief It tests default settings
    def test_merge_group_tocut9(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.tocut = ["NXentry"]
        self.assertEqual(
            el.collect([
                "<definition/>",
                "<definition><group type='NXentry' name='entry2'>"
                "<group type='NXtransformations'/></group></definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        checkxmls(
            self,
            el.toString(),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry2" type="NXentry">'
            '<group type="NXtransformations" /></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_merge_group_tocut10(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.tocut = ["NXentry", "NXtransformations"]
        self.assertEqual(
            el.collect(
                ["<definition/>",
                 "<definition><group type='NXentry' name='entry2'>"
                 "<group type='NXtransformations' name='transformations'/>"
                 "</group></definition>"]), None)
        self.assertEqual(el.merge(), None)
        checkxmls(
            self,
            el.toString(),
            '<?xml version=\'1.0\' encoding=\'utf8\'?>'
            '<definition><group name="entry2" type="NXentry" /></definition>')

    # test collect
    # \brief It tests default settings
    def test_merge_group_tocut11(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.tocut = ["NXentry", "NXtransformations"]
        self.assertEqual(
            el.collect(
                ["<definition/>",
                 "<definition><group type='NXentry' name='entry2'>"
                 "<group type='NXtransformations' name='transformations2'/>"
                 "</group></definition>"]), None)
        self.assertEqual(el.merge(), None)
        checkxmls(
            self,
            el.toString(),
            '<?xml version=\'1.0\' encoding=\'utf8\'?>'
            '<definition><group name="entry2" type="NXentry">'
            '<group name="transformations2" type="NXtransformations" />'
            '</group></definition>')

    # test collect
    # \brief It tests default settings
    def test_merge_group_5(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        self.assertEqual(
            el.collect(
                ["<definition><group type='NXentry'/></definition>"] * 5),
            None)
        self.assertEqual(el.merge(), None)
        checkxmls(
            self,
            el.toString(),
            '<?xml version=\'1.0\' encoding=\'utf8\'?>'
            '<definition><group type="NXentry" />'
            '</definition>')

    # test collect
    # \brief It tests default settings
    def test_merge_group_group(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        self.assertEqual(
            el.collect(
                ["<definition><group type='NXentry'/></definition>",
                 "<definition><group type='NXentry2'/></definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?>'
            '<definition><group type="NXentry" />'
            '<group type="NXentry2" /></definition>')

    # test collect
    # \brief It tests default settings
    def test_merge_group_group_2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        self.assertEqual(
            el.collect(
                ["<definition><group name='entry'/></definition>",
                 "<definition><group type='NXentry2'/></definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry2" /></definition>')

    # test collect
    # \brief It tests default settings
    def test_merge_group_group_3(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        self.assertEqual(
            el.collect(
                ["<definition><group name='entry'/></definition>",
                 "<definition><group name='entry' type='NXentry'/>"
                 "</definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?>'
            '<definition><group name="entry" type="NXentry" /></definition>')

    # test collect
    # \brief It tests default settings
    def test_merge_group_group_4(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        self.assertEqual(
            el.collect([
                "<definition><group name='entry2'/></definition>",
                "<definition><group name='entry' type='NXentry'/>"
                "</definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?>'
            '<definition><group name="entry2" />'
            '<group name="entry" type="NXentry" /></definition>')

    # test collect
    # \brief It tests default settings
    def test_merge_group_field_3(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        self.assertEqual(
            el.collect(
                ["<definition><group type='NXentry'><field type='field'/>"
                 "</group></definition>"] * 3), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?>'
            '<definition><group type="NXentry">'
            '<field type="field" /></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_merge_group_field_4(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        self.assertEqual(
            el.collect(
                ["<definition><group type='NXentry'><field type='field'/>"
                 "</group></definition>"] * 10), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?>'
            '<definition><group type="NXentry">'
            '<field type="field" /></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_merge_group_field_5(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'/></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<field type='field'/></group></definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry">'
            '<field type="field" /></group>'
            '</definition>')

    # test collect
    # \brief It tests default settings
    def test_merge_group_field_name_error(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'/></group></definition>",
                 "<definition><group name='entry' type='NXentry2'>"
                 "<field type='field'/></group></definition>"]), None)
        self.myAssertRaise(IncompatibleNodeError, el.merge)

    # test collect
    # \brief It tests default settings
    def test_merge_single_name(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.singles = []
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'/></group></definition>",
                 "<definition><group name='entry2' type='NXentry2'>"
                 "<field type='field'/></group></definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field" />'
            '</group><group name="entry2" type="NXentry2">'
            '<field type="field" /></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_merge_single_name_error(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.singles = ['group']
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'/></group></definition>",
                 "<definition><group name='entry2' type='NXentry2'>"
                 "<field type='field'/></group></definition>"]), None)
        self.myAssertRaise(IncompatibleNodeError, el.merge)

    # test collect
    # \brief It tests default settings
    def test_merge_single(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.singles = ['field']
        self.assertEqual(
            el.collect(
                ["<definition><group  type='NXentry'><field type='field'/>"
                 "</group></definition>",
                 "<definition><group type='NXentry2'><field type='field'/>"
                 "</group></definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?>'
            '<definition><group type="NXentry">'
            '<field type="field" /></group><group type="NXentry2">'
            '<field type="field" /></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_merge_single_error(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.singles = ['group']
        self.assertEqual(
            el.collect(
                ["<definition><group type='NXentry'><field type='field'/>"
                 "</group></definition>",
                 "<definition><group  type='NXentry2'><field type='field'/>"
                 "</group></definition>"]), None)
        self.myAssertRaise(IncompatibleNodeError, el.merge)

    # test collect
    # \brief It tests default settings
    def test_merge_uniqueText(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.uniqueText = []
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'>My text </field></group></definition>",
                 "<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'>My text 2 </field></group>"
                 "</definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?>'
            '<definition><group name="entry" type="NXentry">'
            '<field type="field">My text \nMy text 2 </field></group>'
            '</definition>')

    # test collect
    # \brief It tests default settings
    def test_merge_uniqueText_error(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.uniqueText = ['field']
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'>My text </field></group></definition>",
                 "<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'>My text 2 </field></group>"
                 "</definition>"]),
            None)
        self.myAssertRaise(IncompatibleNodeError, el.merge)

    # test collect
    # \brief It tests default settings
    def test_merge_uniqueText_error_2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.uniqueText = ['datasource', 'field']
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'>My text </field></group></definition>",
                 "<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'>My text 2 </field></group>"
                 "</definition>"]),
            None)
        self.myAssertRaise(IncompatibleNodeError, el.merge)

    # test collect
    # \brief It tests default settings
    def test_merge_children(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.children = {
            "datasource": ("record", "doc", "device", "database",
                           "query", "door"),
            "attribute": ("datasource", "strategy", "enumeration", "doc"),
            "definition": ("group", "field", "attribute", "link", "component",
                           "doc", "symbols"),
            "dimensions": ("dim", "doc"),
            "field": ("attribute", "datasource", "doc", "dimensions",
                      "enumeration", "strategy"),
            "group": ("field", "group", "attribute", "link", "component",
                      "doc"),
            "link": ("doc")
        }
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'/></group></definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field" />'
            '</group></definition>')

    # test collect
    # \brief It tests default settings
    def test_merge_children_error(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.children = {
            "datasource": ("record", "doc", "device", "database", "query",
                           "door"),
            "attribute": ("datasource", "strategy", "enumeration", "doc"),
            "definition": ("group", "field", "attribute", "link", "component",
                           "doc", "symbols"),
            "dimensions": ("dim", "doc"),
            "field": ("attribute", "datasource", "doc", "dimensions",
                      "enumeration", "strategy"),
            "group": ("group", "attribute", "link", "component", "doc"),
            "link": ("doc")
        }

        self.assertEqual(
            el.collect(["<definition><group  name='entry' type='NXentry'>"
                        "<field type='field'/></group></definition>"]), None)
        self.myAssertRaise(IncompatibleNodeError, el.merge)

    # test collect
    # \brief It tests default settings
    def test_merge_children_2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.children = {
            "datasource": ("record", "doc", "device", "database",
                           "query", "door"),
            "attribute": ("datasource", "strategy", "enumeration", "doc"),
            "definition": ("group", "field", "attribute", "link",
                           "component", "doc", "symbols"),
            "dimensions": ("dim", "doc"),
            "field": ("attribute", "datasource", "doc", "dimensions",
                      "enumeration", "strategy"),
            "group": ("field", "group", "attribute", "link", "component",
                      "doc"),
            "link": ("doc")
        }
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'/></group></definition>",
                 "<definition><group  name='entry' type='NXentry'>"
                 "<field /></group></definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field" />'
            '</group></definition>')

    # test collect
    # \brief It tests default settings
    def test_merge_children_error_2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.children = {
            "datasource": ("record", "doc", "device", "database", "query",
                           "door"),
            "attribute": ("datasource", "strategy", "enumeration", "doc"),
            "definition": ("group", "field", "attribute", "link", "component",
                           "doc", "symbols"),
            "dimensions": ("dim", "doc"),
            "field": ("attribute", "datasource", "doc", "dimensions",
                      "enumeration", "strategy"),
            "group": ("group", "attribute", "link", "component", "doc"),
            "link": ("doc")
        }

        self.assertEqual(
            el.collect(
                ["<definition><group name='entry' type='NXentry'>"
                 "<field type='field'/></group></definition>",
                 "<definition><group  name='entry' type='NXentry'>"
                 "<field /></group></definition>"]), None)
        self.myAssertRaise(IncompatibleNodeError, el.merge)

    # test collect
    # \brief It tests default settings
    def test_switch_stepdatasources_none(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        self.assertEqual(el.switchdatasources, [])
        self.assertEqual(el.switchable, ["field", 'attribute'])
        self.assertEqual(el.modesToSwitch, {'INIT': 'STEP', 'FINAL': 'STEP'})

        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'><datasource name='ds1'/>"
                 "<strategy mode='INIT' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds1'/>"
                 "<strategy mode='INIT'/></attribute></group></definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '<datasource name="ds1" /><strategy mode="INIT" /></field>'
            '<attribute type="field2"><datasource name="ds1" />'
            '<strategy mode="INIT" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_stepdatasources_step_one(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.switchdatasources = ['ds1']
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'><datasource name='ds1'/>"
                 "<strategy mode='INIT' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'/>"
                 "<strategy mode='FINAL'/></attribute></group>"
                 "</definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '<datasource name="ds1" /><strategy mode="STEP" />'
            '</field><attribute type="field2"><datasource name="ds2" />'
            '<strategy mode="FINAL" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_stepdatasources_step_one_2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.switchdatasources = ['ds2']
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'><datasource name='ds1'/>"
                 "<strategy mode='INIT' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'/>"
                 "<strategy mode='FINAL'/></attribute></group></definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '<datasource name="ds1" /><strategy mode="INIT" /></field>'
            '<attribute type="field2"><datasource name="ds2" />'
            '<strategy mode="STEP" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_stepdatasources_step_two(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.switchdatasources = ['ds1']
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'><datasource name='ds1'/>"
                 "<strategy mode='INIT' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds1'/>"
                 "<strategy mode='FINAL'/></attribute></group></definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '<datasource name="ds1" /><strategy mode="STEP" /></field>'
            '<attribute type="field2"><datasource name="ds1" />'
            '<strategy mode="STEP" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_stepdatasources_step_two_2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.switchdatasources = ['ds1', 'ds2']
        self.assertEqual(el.switchable, ["field", 'attribute'])
        self.assertEqual(el.modesToSwitch, {'INIT': 'STEP', 'FINAL': 'STEP'})
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'><datasource name='ds1'/>"
                 "<strategy mode='INIT' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'/>"
                 "<strategy mode='FINAL'/></attribute></group>"
                 "</definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '<datasource name="ds1" /><strategy mode="STEP" />'
            '</field><attribute type="field2"><datasource name="ds2" />'
            '<strategy mode="STEP" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_stepdatasources_step_tags(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.switchdatasources = ['ds1', 'ds2']
        el.switchable = ["field2", 'attribute1']
        self.assertEqual(el.modesToSwitch, {'INIT': 'STEP', 'FINAL': 'STEP'})
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'><datasource name='ds1'/>"
                 "<strategy mode='INIT' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'/>"
                 "<strategy mode='FINAL'/></attribute></group></definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '<datasource name="ds1" /><strategy mode="INIT" /></field>'
            '<attribute type="field2"><datasource name="ds2" />'
            '<strategy mode="FINAL" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_stepdatasources_step_tags_2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.switchdatasources = ['ds1', 'ds2']
        el.switchable = ["field", 'attribute1']
        self.assertEqual(el.modesToSwitch, {'INIT': 'STEP', 'FINAL': 'STEP'})
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'><datasource name='ds1'/>"
                 "<strategy mode='INIT' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'/>"
                 "<strategy mode='FINAL'/></attribute></group></definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '<datasource name="ds1" /><strategy mode="STEP" /></field>'
            '<attribute type="field2"><datasource name="ds2" />'
            '<strategy mode="FINAL" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_stepdatasources_step_modes(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.switchdatasources = ['ds1', 'ds2']
        el.switchable = ["field", 'attribute']
        el.modesToSwitch = {}
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'><datasource name='ds1'/>"
                 "<strategy mode='INIT' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'/>"
                 "<strategy mode='FINAL'/></attribute></group></definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?>'
            '<definition><group name="entry" type="NXentry">'
            '<field type="field"><datasource name="ds1" />'
            '<strategy mode="INIT" /></field><attribute type="field2">'
            '<datasource name="ds2" /><strategy mode="FINAL" /></attribute>'
            '</group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_stepdatasources_step_modes_1(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.switchdatasources = ['ds1', 'ds2']
        el.switchable = ["field", 'attribute']
        el.modesToSwitch = {'INIT': 'STEP'}
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'><datasource name='ds1'/>"
                 "<strategy mode='INIT' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'/>"
                 "<strategy mode='FINAL'/></attribute></group></definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '<datasource name="ds1" /><strategy mode="STEP" /></field>'
            '<attribute type="field2"><datasource name="ds2" />'
            '<strategy mode="FINAL" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_stepdatasources_step_modes_2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.switchdatasources = ['ds1', 'ds2']
        el.switchable = ["field", 'attribute']
        el.modesToSwitch = {'FINAL': 'STEP'}
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'><datasource name='ds1'/>"
                 "<strategy mode='INIT' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'/>"
                 "<strategy mode='FINAL'/></attribute></group></definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '<datasource name="ds1" /><strategy mode="INIT" /></field>'
            '<attribute type="field2"><datasource name="ds2" />'
            '<strategy mode="STEP" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_stepdatasources_none_var(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        self.assertEqual(el.switchdatasources, [])
        self.assertEqual(el.switchable, ["field", 'attribute'])
        self.assertEqual(el.modesToSwitch, {'INIT': 'STEP', 'FINAL': 'STEP'})

        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'>$datasources.ds1<strategy mode='INIT' />"
                 "</field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'>$datasources.ds1"
                 "<strategy mode='INIT'/></attribute></group></definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '$datasources.ds1<strategy mode="INIT" /></field>'
            '<attribute type="field2">$datasources.ds1'
            '<strategy mode="INIT" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_stepdatasources_step_one_var(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.switchdatasources = ['ds1']
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'>$datasources.ds1"
                 "<strategy mode='INIT' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'/>"
                 "<strategy mode='FINAL'/></attribute></group></definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '$datasources.ds1<strategy mode="STEP" /></field>'
            '<attribute type="field2"><datasource name="ds2" />'
            '<strategy mode="FINAL" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_stepdatasources_step_one_2_var(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.switchdatasources = ['ds2']
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'>$datasources.ds1<strategy mode='INIT' />"
                 "</field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'/>"
                 "<strategy mode='FINAL'/></attribute></group></definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '$datasources.ds1<strategy mode="INIT" /></field>'
            '<attribute type="field2"><datasource name="ds2" />'
            '<strategy mode="STEP" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_stepdatasources_step_two_var(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.switchdatasources = ['ds1']
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'>$datasources.ds1"
                 "<strategy mode='INIT' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'>$datasources.ds1"
                 "<strategy mode='FINAL'/></attribute></group></definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '$datasources.ds1<strategy mode="STEP" /></field>'
            '<attribute type="field2">$datasources.ds1'
            '<strategy mode="STEP" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_stepdatasources_step_two_2_var(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.switchdatasources = ['ds1', 'ds2']
        self.assertEqual(el.switchable, ["field", 'attribute'])
        self.assertEqual(el.modesToSwitch, {'INIT': 'STEP', 'FINAL': 'STEP'})
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'>$datasources.ds1<strategy mode='INIT' />"
                 "</field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'/>"
                 "<strategy mode='FINAL'/></attribute></group>"
                 "</definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '$datasources.ds1<strategy mode="STEP" /></field>'
            '<attribute type="field2"><datasource name="ds2" />'
            '<strategy mode="STEP" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_stepdatasources_step_tags_var(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.switchdatasources = ['ds1', 'ds2']
        el.switchable = ["field2", 'attribute1']
        self.assertEqual(el.modesToSwitch, {'INIT': 'STEP', 'FINAL': 'STEP'})
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'>$datasources.ds1"
                 "<strategy mode='INIT' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'/>"
                 "<strategy mode='FINAL'/></attribute></group></definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '$datasources.ds1<strategy mode="INIT" /></field>'
            '<attribute type="field2"><datasource name="ds2" />'
            '<strategy mode="FINAL" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_stepdatasources_step_tags_2_var(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.switchdatasources = ['ds1', 'ds2']
        el.switchable = ["field", 'attribute1']
        self.assertEqual(el.modesToSwitch, {'INIT': 'STEP', 'FINAL': 'STEP'})
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'>$datasources.ds1"
                 "<strategy mode='INIT' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'/>"
                 "<strategy mode='FINAL'/></attribute></group></definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        checkxmls(
            self, el.toString(),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '$datasources.ds1<strategy mode="STEP" /></field>'
            '<attribute type="field2"><datasource name="ds2" />'
            '<strategy mode="FINAL" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_stepdatasources_step_postrun_tags_2_var(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.switchdatasources = ['ds1', 'ds2']
        el.switchable = ["field", 'attribute']
        el.modesToSwitch = {'INIT': 'STEP', 'FINAL': 'POSTRUN'}
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'>$datasources.ds1"
                 "<strategy mode='INIT' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'/>"
                 "<strategy mode='FINAL'/></attribute></group></definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '$datasources.ds1<strategy mode="STEP" /></field>'
            '<attribute type="field2"><datasource name="ds2" />'
            '<strategy mode="POSTRUN" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_stepdatasources_step_modes_var(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.switchdatasources = ['ds1', 'ds2']
        el.switchable = ["field", 'attribute']
        el.modesToSwitch = {}
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'>$datasources.ds1<strategy mode='INIT' />"
                 "</field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'/>"
                 "<strategy mode='FINAL'/></attribute></group></definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '$datasources.ds1<strategy mode="INIT" /></field>'
            '<attribute type="field2"><datasource name="ds2" />'
            '<strategy mode="FINAL" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_stepdatasources_step_modes_var_1(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.switchdatasources = ['ds1', 'ds2']
        el.switchable = ["field", 'attribute']
        el.modesToSwitch = {'INIT': 'STEP'}
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'>$datasources.ds1"
                 "<strategy mode='INIT' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'/>"
                 "<strategy mode='FINAL'/></attribute></group></definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '$datasources.ds1<strategy mode="STEP" /></field>'
            '<attribute type="field2"><datasource name="ds2" />'
            '<strategy mode="FINAL" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_stepdatasources_postrun_modes_var(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.switchdatasources = ['ds1', 'ds2']
        el.switchable = ["field", 'attribute']
        el.modesToSwitch = {'STEP': 'POSTRUN'}
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'>$datasources.ds1"
                 "<strategy mode='STEP' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'/>"
                 "<strategy mode='FINAL'/></attribute></group>"
                 "</definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '$datasources.ds1<strategy mode="POSTRUN" /></field>'
            '<attribute type="field2"><datasource name="ds2" />'
            '<strategy mode="FINAL" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_stepdatasources_step_modes_2_var(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.switchdatasources = ['ds1', 'ds2']
        el.switchable = ["field", 'attribute']
        el.modesToSwitch = {'FINAL': 'STEP'}
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'>$datasources.ds1"
                 "<strategy mode='INIT' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'/>"
                 "<strategy mode='FINAL'/></attribute></group></definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry">'
            '<field type="field">$datasources.ds1'
            '<strategy mode="INIT" /></field><attribute type="field2">'
            '<datasource name="ds2" /><strategy mode="STEP" />'
            '</attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_stepdatasources_step_one_var_py(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.switchdatasources = ['ds1']
        self.assertEqual(
            el.collect(
                ["<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'>"
                 "<datasource name='ds1'/></datasource>"
                 "<strategy mode='FINAL'/></attribute></group>"
                 "</definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><attribute type="field2">'
            '<datasource name="ds2"><datasource name="ds1" /></datasource>'
            '<strategy mode="STEP" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_stepdatasources_step_one_var_py2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.switchdatasources = ['ds2']
        self.assertEqual(
            el.collect(
                ["<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'>"
                 "<datasource name='ds1'/></datasource>"
                 "<strategy mode='INIT'/></attribute></group>"
                 "</definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><attribute type="field2">'
            '<datasource name="ds2"><datasource name="ds1" /></datasource>'
            '<strategy mode="STEP" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_stepdatasources_step_one_var_py3(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.switchdatasources = ['ds3']
        self.assertEqual(
            el.collect(
                ["<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'>"
                 "<datasource name='ds1'/></datasource>"
                 "<strategy mode='FINAL'/></attribute>"
                 "</group></definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><attribute type="field2">'
            '<datasource name="ds2"><datasource name="ds1" /></datasource>'
            '<strategy mode="FINAL" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_stepdatasources_step_one_var_py4(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.switchdatasources = ['ds1']
        self.assertEqual(
            el.collect(
                ["<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'>"
                 "$datasources.ds1</datasource><strategy mode='FINAL'/>"
                 "</attribute></group></definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><attribute type="field2">'
            '<datasource name="ds2">$datasources.ds1</datasource>'
            '<strategy mode="STEP" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_stepdatasources_step_one_var_py5(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.switchdatasources = ['ds2']
        self.assertEqual(
            el.collect(
                ["<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'>"
                 "$datasources.ds1</datasource><strategy mode='INIT'/>"
                 "</attribute></group></definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><attribute type="field2">'
            '<datasource name="ds2">$datasources.ds1</datasource>'
            '<strategy mode="STEP" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_stepdatasources_step_one_var_py6(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.switchdatasources = ['ds3']
        self.assertEqual(
            el.collect(
                ["<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'>"
                 "$datasources.ds1</datasource><strategy mode='FINAL'/>"
                 "</attribute></group></definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><attribute type="field2">'
            '<datasource name="ds2">$datasources.ds1</datasource>'
            '<strategy mode="FINAL" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_linkdatasources_none(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        self.assertEqual(el.linkdatasources, [])
        self.assertEqual(el.linkable, ["field"])

        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'><datasource name='ds1'/>"
                 "<strategy mode='INIT' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds1'/>"
                 "<strategy mode='INIT'/></attribute></group>"
                 "</definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '<datasource name="ds1" /><strategy mode="INIT" /></field>'
            '<attribute type="field2"><datasource name="ds1" />'
            '<strategy mode="INIT" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_linkdatasources_ds1_nofieldname(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.linkdatasources = ["ds1"]
        self.assertEqual(el.linkable, ["field"])

        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'><datasource name='ds1'/>"
                 "<strategy mode='INIT' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds1'/>"
                 "<strategy mode='INIT'/></attribute></group></definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '<datasource name="ds1" /><strategy mode="INIT" /></field>'
            '<attribute type="field2"><datasource name="ds1" />'
            '<strategy mode="INIT" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_linkdatasources_ds1(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.linkdatasources = ["ds1"]
        self.assertEqual(el.linkable, ["field"])

        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field name='myfield' type='field'><datasource name='ds1'/>"
                 "<strategy mode='INIT' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds1'/>"
                 "<strategy mode='INIT'/></attribute></group>"
                 "</definition>"]), None)
        self.assertEqual(el.merge(), None)
        checkxmls(
            self, el.toString(),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry">'
            '<field name="myfield" type="field"><datasource name="ds1" />'
            '<strategy mode="INIT" /></field><attribute type="field2">'
            '<datasource name="ds1" /><strategy mode="INIT" /></attribute>'
            '<group name="data" type="NXdata">'
            '<link name="ds1" target="/entry:NXentry/myfield" />'
            '</group></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_linkdatasources_ds1_withdata(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.linkdatasources = ["ds1"]
        self.assertEqual(el.linkable, ["field"])

        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field name='myfield' type='field'><datasource name='ds1'/>"
                 "<strategy mode='STEP' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds1'/>"
                 "<strategy mode='INIT'/></attribute>"
                 "<group name='data' type='NXdata' />"
                 "</group></definition>"]), None)
        self.assertEqual(el.merge(), None)
        checkxmls(
            self,
            el.toString(),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry">'
            '<field name="myfield" type="field"><datasource name="ds1" />'
            '<strategy mode="STEP" /></field><attribute type="field2">'
            '<datasource name="ds1" /><strategy mode="INIT" /></attribute>'
            '<group name="data" type="NXdata">'
            '<link name="ds1" target="/entry:NXentry/myfield" />'
            '</group></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_linkdatasources_ds1_twofields(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.linkdatasources = ["ds1"]
        self.assertEqual(el.linkable, ["field"])

        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<group  name='instrument' type='NXinstrument'>"
                 "<field name='myfield' type='field'><datasource name='ds2'/>"
                 "<strategy mode='STEP' /></field></group></group>"
                 "</definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<field name='mf' type='field2'><datasource name='ds1'/>"
                 "<strategy mode='INIT'/></field>"
                 "<group name='data' type='NXdata' /></group></definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        checkxmls(
            self,
            el.toString(),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry">'
            '<group name="instrument" type="NXinstrument">'
            '<field name="myfield" type="field"><datasource name="ds2" />'
            '<strategy mode="STEP" /></field></group>'
            '<field name="mf" type="field2"><datasource name="ds1" />'
            '<strategy mode="INIT" /></field>'
            '<group name="data" type="NXdata">'
            '<link name="ds1" target="/entry:NXentry/mf" />'
            '</group></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_linkdatasources_ds1_twolinks(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.linkdatasources = ["ds1", "ds2"]
        self.assertEqual(el.linkable, ["field"])

        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<group  name='instrument' type='NXinstrument'>"
                 "<field name='myfield' type='field'>"
                 "<datasource name='ds2'/><strategy mode='STEP' />"
                 "</field></group></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<field name='mf' type='field2'><datasource name='ds1'/>"
                 "<strategy mode='INIT'/></field>"
                 "<group name='data' type='NXdata' /></group></definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        checkxmls(
            self,
            el.toString(),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry">'
            '<group name="instrument" type="NXinstrument">'
            '<field name="myfield" type="field"><datasource name="ds2" />'
            '<strategy mode="STEP" /></field></group>'
            '<field name="mf" type="field2"><datasource name="ds1" />'
            '<strategy mode="INIT" /></field>'
            '<group name="data" type="NXdata">'
            '<link name="ds2" '
            'target="/entry:NXentry/instrument:NXinstrument/myfield" />'
            '<link name="ds1" target="/entry:NXentry/mf" />'
            '</group></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_linkdatasources_ds1_twoduplinks(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.linkdatasources = ["ds1"]
        self.assertEqual(el.linkable, ["field"])

        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<group  name='instrument' type='NXinstrument'>"
                 "<field name='myfield' type='field'><datasource name='ds1'/>"
                 "<strategy mode='STEP' /></field></group></group>"
                 "</definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<field name='mf' type='field2'><datasource name='ds1'/>"
                 "<strategy mode='INIT'/></field>"
                 "<group name='data' type='NXdata' /></group>"
                 "</definition>"]), None)
        self.assertEqual(el.merge(), None)
        checknxmls(
            self,
            el.toString(),
            [
                '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
                '<group name="entry" type="NXentry">'
                '<group name="instrument" type="NXinstrument">'
                '<field name="myfield" type="field"><datasource name="ds1" />'
                '<strategy mode="STEP" /></field></group>'
                '<field name="mf" type="field2"><datasource name="ds1" />'
                '<strategy mode="INIT" /></field>'
                '<group name="data" type="NXdata">'
                '<link name="ds1" '
                'target="/entry:NXentry/mf" /></group>'
                '</group></definition>',
                '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
                '<group name="entry" type="NXentry">'
                '<group name="instrument" type="NXinstrument">'
                '<field name="myfield" type="field"><datasource name="ds1" />'
                '<strategy mode="STEP" /></field></group>'
                '<field name="mf" type="field2"><datasource name="ds1" />'
                '<strategy mode="INIT" /></field>'
                '<group name="data" type="NXdata">'
                '<link name="ds1" '
                'target="/entry:NXentry/instrument:NXinstrument/myfield" />'
                '</group>'
                '</group></definition>'
            ]
            )

    # test collect
    # \brief It tests default settings
    def test_linkdatasources_ds1_twolinks_oneexists(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.linkdatasources = ["ds1", "ds2"]
        self.assertEqual(el.linkable, ["field"])

        self.assertEqual(
            el.collect(
                ["<definition><group name='entry' type='NXentry'>"
                 "<group  name='instrument' type='NXinstrument'>"
                 "<field name='myfield' type='field'><datasource name='ds2'/>"
                 "<strategy mode='STEP' /></field></group></group>"
                 "</definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<field name='mf' type='field2'><datasource name='ds1'/>"
                 "<strategy mode='INIT'/></field>"
                 "<group name='data' type='NXdata' >"
                 "<link name='ds1' target='/entry:NXentry'/>"
                 "</group></group></definition>"]), None)
        self.assertEqual(el.merge(), None)
        checkxmls(
            self,
            el.toString(),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry">'
            '<group name="instrument" type="NXinstrument">'
            '<field name="myfield" type="field"><datasource name="ds2" />'
            '<strategy mode="STEP" /></field></group>'
            '<field name="mf" type="field2"><datasource name="ds1" />'
            '<strategy mode="INIT" /></field>'
            '<group name="data" type="NXdata">'
            '<link name="ds1" target="/entry:NXentry" />'
            '<link name="ds2" '
            'target="/entry:NXentry/instrument:NXinstrument/myfield" />'
            '</group></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_canfaildatasources_none(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        self.assertEqual(el.canfaildatasources, [])
        self.assertEqual(el.switchable, ["field", 'attribute'])

        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'><datasource name='ds1'/>"
                 "<strategy canfail='false' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds1'/>"
                 "<strategy canfail='false'/></attribute></group>"
                 "</definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '<datasource name="ds1" /><strategy canfail="false" /></field>'
            '<attribute type="field2"><datasource name="ds1" />'
            '<strategy canfail="false" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_canfaildatasources_step_one(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.canfaildatasources = ['ds1']
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'><datasource name='ds1'/>"
                 "<strategy canfail='false' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'/>"
                 "<strategy canfail='false'/></attribute></group>"
                 "</definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '<datasource name="ds1" /><strategy canfail="true" />'
            '</field><attribute type="field2"><datasource name="ds2" />'
            '<strategy canfail="false" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_canfaildatasources_step_one_2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.canfaildatasources = ['ds2']
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'><datasource name='ds1'/>"
                 "<strategy canfail='false' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'/>"
                 "<strategy canfail='false'/></attribute></group>"
                 "</definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '<datasource name="ds1" /><strategy canfail="false" /></field>'
            '<attribute type="field2"><datasource name="ds2" />'
            '<strategy canfail="true" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_canfaildatasources_step_two(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.canfaildatasources = ['ds1']
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'><datasource name='ds1'/>"
                 "<strategy canfail='false' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds1'/>"
                 "<strategy canfail='false'/></attribute></group>"
                 "</definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '<datasource name="ds1" /><strategy canfail="true" /></field>'
            '<attribute type="field2"><datasource name="ds1" />'
            '<strategy canfail="true" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_canfaildatasources_step_two_2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.canfaildatasources = ['ds1', 'ds2']
        self.assertEqual(el.switchable, ["field", 'attribute'])
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'><datasource name='ds1'/>"
                 "<strategy canfail='false' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'/>"
                 "<strategy canfail='false'/></attribute></group>"
                 "</definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '<datasource name="ds1" /><strategy canfail="true" />'
            '</field><attribute type="field2"><datasource name="ds2" />'
            '<strategy canfail="true" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_canfaildatasources_step_tags(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.canfaildatasources = ['ds1', 'ds2']
        el.switchable = ["field2", 'attribute1']
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'><datasource name='ds1'/>"
                 "<strategy canfail='false' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'/>"
                 "<strategy canfail='false'/></attribute></group>"
                 "</definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '<datasource name="ds1" /><strategy canfail="false" /></field>'
            '<attribute type="field2"><datasource name="ds2" />'
            '<strategy canfail="false" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_canfaildatasources_step_tags_2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.canfaildatasources = ['ds1', 'ds2']
        el.switchable = ["field", 'attribute1']
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'><datasource name='ds1'/>"
                 "<strategy canfail='false' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'/>"
                 "<strategy canfail='false'/></attribute>"
                 "</group></definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '<datasource name="ds1" /><strategy canfail="true" /></field>'
            '<attribute type="field2"><datasource name="ds2" />'
            '<strategy canfail="false" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_canfaildatasources_none_var(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        self.assertEqual(el.canfaildatasources, [])
        self.assertEqual(el.switchable, ["field", 'attribute'])
        self.assertEqual(el.modesToSwitch, {'INIT': 'STEP', 'FINAL': 'STEP'})

        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'>$datasources.ds1"
                 "<strategy canfail='false' />"
                 "</field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'>$datasources.ds1"
                 "<strategy canfail='false'/></attribute></group>"
                 "</definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '$datasources.ds1<strategy canfail="false" /></field>'
            '<attribute type="field2">$datasources.ds1'
            '<strategy canfail="false" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_canfaildatasources_step_one_var(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.canfaildatasources = ['ds1']
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'>$datasources.ds1"
                 "<strategy canfail='false' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'/>"
                 "<strategy canfail='false'/></attribute>"
                 "</group></definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '$datasources.ds1<strategy canfail="true" /></field>'
            '<attribute type="field2"><datasource name="ds2" />'
            '<strategy canfail="false" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_canfaildatasources_step_one_2_var(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.canfaildatasources = ['ds2']
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'>$datasources.ds1"
                 "<strategy canfail='false' />"
                 "</field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'/>"
                 "<strategy canfail='false'/></attribute></group>"
                 "</definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '$datasources.ds1<strategy canfail="false" /></field>'
            '<attribute type="field2"><datasource name="ds2" />'
            '<strategy canfail="true" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_canfaildatasources_step_two_var(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.canfaildatasources = ['ds1']
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'>$datasources.ds1"
                 "<strategy canfail='false' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'>$datasources.ds1"
                 "<strategy canfail='false'/></attribute></group>"
                 "</definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '$datasources.ds1<strategy canfail="true" /></field>'
            '<attribute type="field2">$datasources.ds1'
            '<strategy canfail="true" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_canfaildatasources_step_two_2_var(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.canfaildatasources = ['ds1', 'ds2']
        self.assertEqual(el.switchable, ["field", 'attribute'])
        self.assertEqual(el.modesToSwitch, {'INIT': 'STEP', 'FINAL': 'STEP'})
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'>$datasources.ds1"
                 "<strategy canfail='false' />"
                 "</field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'/>"
                 "<strategy canfail='false'/></attribute></group>"
                 "</definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '$datasources.ds1<strategy canfail="true" /></field>'
            '<attribute type="field2"><datasource name="ds2" />'
            '<strategy canfail="true" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_canfaildatasources_step_tags_var(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.canfaildatasources = ['ds1', 'ds2']
        el.switchable = ["field2", 'attribute1']
        self.assertEqual(el.modesToSwitch, {'INIT': 'STEP', 'FINAL': 'STEP'})
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'>$datasources.ds1"
                 "<strategy canfail='false' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'/>"
                 "<strategy canfail='false'/></attribute></group>"
                 "</definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '$datasources.ds1<strategy canfail="false" /></field>'
            '<attribute type="field2"><datasource name="ds2" />'
            '<strategy canfail="false" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_canfaildatasources_step_tags_2_var(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.canfaildatasources = ['ds1', 'ds2']
        el.switchable = ["field", 'attribute1']
        self.assertEqual(el.modesToSwitch, {'INIT': 'STEP', 'FINAL': 'STEP'})
        self.assertEqual(
            el.collect(
                ["<definition><group  name='entry' type='NXentry'>"
                 "<field type='field'>$datasources.ds1"
                 "<strategy canfail='false' /></field></group></definition>",
                 "<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'/>"
                 "<strategy canfail='false'/></attribute></group>"
                 "</definition>"]),
            None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><field type="field">'
            '$datasources.ds1<strategy canfail="true" /></field>'
            '<attribute type="field2"><datasource name="ds2" />'
            '<strategy canfail="false" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_canfaildatasources_step_one_var_py(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.canfaildatasources = ['ds1']
        self.assertEqual(
            el.collect(
                ["<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'>"
                 "<datasource name='ds1'/></datasource>"
                 "<strategy canfail='false'/></attribute></group>"
                 "</definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><attribute type="field2">'
            '<datasource name="ds2"><datasource name="ds1" /></datasource>'
            '<strategy canfail="true" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_canfaildatasources_step_one_var_py2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.canfaildatasources = ['ds2']
        self.assertEqual(
            el.collect(
                ["<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'>"
                 "<datasource name='ds1'/></datasource>"
                 "<strategy canfail='false'/></attribute></group>"
                 "</definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><attribute type="field2">'
            '<datasource name="ds2"><datasource name="ds1" /></datasource>'
            '<strategy canfail="true" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_canfaildatasources_step_one_var_py3(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.canfaildatasources = ['ds3']
        self.assertEqual(
            el.collect(
                ["<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'>"
                 "<datasource name='ds1'/></datasource>"
                 "<strategy canfail='false'/></attribute>"
                 "</group></definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><attribute type="field2">'
            '<datasource name="ds2"><datasource name="ds1" /></datasource>'
            '<strategy canfail="false" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_canfaildatasources_step_one_var_py4(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.canfaildatasources = ['ds1']
        self.assertEqual(
            el.collect(
                ["<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'>"
                 "$datasources.ds1</datasource><strategy canfail='false'/>"
                 "</attribute></group></definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><attribute type="field2">'
            '<datasource name="ds2">$datasources.ds1</datasource>'
            '<strategy canfail="true" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_canfaildatasources_step_one_var_py5(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.canfaildatasources = ['ds2']
        self.assertEqual(
            el.collect(
                ["<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'>"
                 "$datasources.ds1</datasource><strategy canfail='false'/>"
                 "</attribute></group></definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><attribute type="field2">'
            '<datasource name="ds2">$datasources.ds1</datasource>'
            '<strategy canfail="true" /></attribute></group></definition>')

    # test collect
    # \brief It tests default settings
    def test_switch_canfaildatasources_step_one_var_py6(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Merger()
        el.canfaildatasources = ['ds3']
        self.assertEqual(
            el.collect(
                ["<definition><group name='entry' type='NXentry'>"
                 "<attribute type='field2'><datasource name='ds2'>"
                 "$datasources.ds1</datasource><strategy canfail='false'/>"
                 "</attribute></group></definition>"]), None)
        self.assertEqual(el.merge(), None)
        self.assertEqual(
            el.toString().replace("?>\n<", "?><"),
            '<?xml version=\'1.0\' encoding=\'utf8\'?><definition>'
            '<group name="entry" type="NXentry"><attribute type="field2">'
            '<datasource name="ds2">$datasources.ds1</datasource>'
            '<strategy canfail="false" /></attribute></group></definition>')


if __name__ == '__main__':
    unittest.main()
