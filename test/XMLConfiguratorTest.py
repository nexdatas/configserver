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
## \package test nexdatas
## \file XMLConfiguratorTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import subprocess
import random
import struct
import binascii
import time

## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


from mcs.XMLConfigurator  import XMLConfigurator

## test fixture
class XMLConfiguratorTest(unittest.TestCase):

    ## constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        try:
            # random seed
            self.seed  = long(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            import time
            ## random seed
            self.seed  = long(time.time() * 256) # use fractional seconds
         
        self.__rnd = random.Random(self.seed)

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

        self.__args = '{"host":"localhost", "db":"ndts", "read_default_file":"/etc/my.cnf", "use_unicode":true}'


    ## test starter
    # \brief Common set up
    def setUp(self):
        print "\nsetting up..."
        print "SEED =", self.seed 

    ## test closer
    # \brief Common tear down
    def tearDown(self):
        print "tearing down ..."

    ## opens configurator
    # \param args connection arguments
    # \returns XMLConfigurator instance   
    def openConfig(self, args):
        xmlc = XMLConfigurator()
        xmlc.jsonSettings = args
        print args
        xmlc.open()
        return xmlc

    ## closes configurator
    # \param xmlc XMLConfigurator instance   
    def closeConfig(self, xmlc):
        xmlc.close()

    ## scanRecord test
    # \brief It tests recording of simple h5 file
    def test_openClose(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        xmlc = self.openConfig(self.__args)
        self.closeConfig(xmlc)

if __name__ == '__main__':
    unittest.main()
