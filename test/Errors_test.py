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
# \package test nexdatas
# \file ErrorsTest.py
# unittests for Error classes
#
import unittest
# import os
import sys
# import subprocess
# import random
# import struct
# import numpy


from nxsconfigserver.Errors import (
    IncompatibleNodeError, UndefinedTagError, NonregisteredDBRecordError)


if sys.version_info > (3,):
    long = int


# test fixture
class ErrorsTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

    # test starter
    # \brief Common set up
    def setUp(self):
        # file handle
        print("\nsetting up...")

    # test closer
    # \brief Common tear down
    def tearDown(self):
        print("tearing down ...")

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

    # IncompatibleNodeError test
    # \brief It tests default settings
    def test_IncompatibleNodeError(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        value = 'ble ble'
        err = IncompatibleNodeError(value)
        self.assertTrue(isinstance(err, Exception))
        self.assertEqual(err.value, value)
        self.assertEqual(err.nodes, [])
        self.assertEqual(err.__str__(), value.__repr__())

    # IncompatibleNodeError test
    # \brief It tests default settings
    def test_IncompatibleNodeError_nodes(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        value = 1234
        nodes = ['asdads1234']
        err = IncompatibleNodeError(value, nodes)
        self.assertTrue(isinstance(err, Exception))
        self.assertEqual(err.value, value)
        self.assertEqual(err.nodes, nodes)
        self.assertEqual(err.__str__(), value.__repr__())

    # UndefinedTagError test
    # \brief It tests default settings
    def test_UndefinedTagError(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        err = UndefinedTagError()
        self.assertTrue(isinstance(err, Exception))

    # NonregisteredDBRecordError test
    # \brief It tests default settings
    def test_NonregisteredDBRecordError(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        err = NonregisteredDBRecordError()
        self.assertTrue(isinstance(err, Exception))


if __name__ == '__main__':
    unittest.main()
