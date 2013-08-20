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
## \file XMLConfigServerTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import subprocess
import random

import PyTango

import ServerSetUp
import XMLConfiguratorTest
from ndtsconfigserver import XMLConfigurator

## test fixture
class XMLConfigServerTest(XMLConfiguratorTest.XMLConfiguratorTest):

    ## constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        XMLConfiguratorTest.XMLConfiguratorTest.__init__(self, methodName)

        self._sv = ServerSetUp.ServerSetUp()



    ## test starter
    # \brief Common set up of Tango Server
    def setUp(self):
        self._sv.setUp()
        print "SEED =", self.seed 

    ## test closer
    # \brief Common tear down oif Tango Server
    def tearDown(self): 
        self._sv.tearDown()
        XMLConfiguratorTest.XMLConfiguratorTest.tearDown(self)
        
    ## opens config server
    # \param args connection arguments
    # \returns XMLConfigServer instance   
    def openWriter(self, args):

        xmlc = PyTango.DeviceProxy(self._sv.new_device_info_writer.name)
        xmlc.JSONSettings = args
        self.assertEqual(xmlc.state(), PyTango.DevState.ON)
        
        xmlc.Open()
        
        self.assertEqual(xmlc.state(), PyTango.DevState.OPEN)
        
        return xmlc


    ## closes opens config server
    # \param xmlc XMLConfigurator instance   
    def closeWriter(self, xmlc):
        self.assertEqual(xmlc.state(), PyTango.DevState.OPEN)

        xmlc.Close()
        self.assertEqual(xmlc.state(), PyTango.DevState.ON)
                



#    ## performs one record step
#    def record(self, tdw, string):
#        tdw.Record(string)

if __name__ == '__main__':
    unittest.main()

