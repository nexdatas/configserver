#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2014 DESY, Jan Kotanski <jkotan@mail.desy.de>
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


from nxsconfigserver.XMLConfigurator  import XMLConfigurator
from nxsconfigserver.Merger import Merger
from nxsconfigserver.Errors import (NonregisteredDBRecordError, UndefinedTagError, 
                                     IncompatibleNodeError)
import nxsconfigserver

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
        self.__cmps = []
        self.__ds = []
        self.__man = []
        self.children = ("record", "doc", "device", "database", "query", "datasource", "result")
        
    ## test starter
    # \brief Common set up
    def setUp(self):
        print "\nsetting up..."
        print "SEED =", self.seed 

    ## test closer
    # \brief Common tear down
    def tearDown(self):
        print "tearing down ..."
        if self.__cmps:
            el = self.openConfig(self.__args)
            for cp in self.__cmps:
                el.deleteComponent(cp)
            el.close()
        if self.__ds:
            el = self.openConfig(self.__args)
            for ds in self.__ds:
                el.deleteDataSource(ds)
            el.close()

        if self.__man:
            el = self.openConfig(self.__args)
            el.setMandatoryComponents(self.__man)
            el.close()

    ## Exception tester
    # \param exception expected exception
    # \param method called method      
    # \param args list with method arguments
    # \param kwargs dictionary with method arguments
    def myAssertRaise(self, exception, method, *args, **kwargs):
        try:
            error =  False
            method(*args, **kwargs)
        except :
            error = True
        self.assertEqual(error, True)




    ## opens configurator
    # \param args connection arguments
    # \returns XMLConfigurator instance   
    def openConfig(self, args):
        xmlc = XMLConfigurator()
        self.assertEqual(xmlc.jsonSettings, "{}")
        self.assertEqual(xmlc.xmlConfig, "")
        xmlc.jsonSettings = args
        print args
        xmlc.open()

        version = xmlc.version
        vv = version.split('.')
        self.revision = long(vv[-1])
        self.version = ".".join(vv[0:3])
        self.label = ".".join(vv[3:-1])

        self.assertEqual(self.version, nxsconfigserver.__version__ )
        self.assertEqual(self.label, xmlc.versionLabel)
        return xmlc

    ## closes configurator
    # \param xmlc XMLConfigurator instance   
    def closeConfig(self, xmlc):
        xmlc.close()

    ## sets xmlconfiguration
    # \param xmlc configuration instance
    # \param xml xml configuration string
    def setXML(self, xmlc, xml):
        xmlc.xmlConfig = xml


    ## gets xmlconfiguration
    # \param xmlc configuration instance
    # \returns xml configuration string
    def getXML(self, xmlc):
        return xmlc.xmlConfig


    ## open close test test
    # \brief It tests XMLConfigurator
    def test_openClose(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        xmlc = self.openConfig(self.__args)
        self.assertEqual(long(xmlc.version.split('.')[-1]),self.revision)
        label = 'asdd@aff.asdf'
        if hasattr(xmlc,"versionLabel"):
            xmlc.versionLabel = label
        self.assertEqual(long(xmlc.version.split('.')[-1]),self.revision)
        if hasattr(xmlc,"versionLabel"):
            self.assertEqual(".".join(xmlc.version.split('.')[3:-1]),label)
        xmlc.close()


    ## comp_available test
    # \brief It tests XMLConfigurator
    def test_comp_available(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        avc = el.availableComponents()

        self.assertTrue(isinstance(avc, list))
        name = "mcs_test_component"
        xml = "<?xml version='1.0'?><definition><group type='NXentry'/></definition>"
        while name in avc:
            name = name + '_1'
#        print avc
        self.setXML(el, xml)
        self.assertEqual(el.storeComponent(name),None)
        self.assertEqual(el.storeComponent(name),None)
        self.__cmps.append(name)
        avc2 = el.availableComponents()
#        print avc2
        self.assertTrue(isinstance(avc2, list))
        for cp in avc:
            self.assertTrue(cp in avc2)
            
        self.assertTrue(name in avc2)
        cpx = el.components([name])
        self.assertEqual(cpx[0], xml)
        
        self.assertEqual(el.deleteComponent(name),None)
        self.__cmps.pop()
        
        avc3 = el.availableComponents()
        self.assertTrue(isinstance(avc3, list))
        for cp in avc:
            self.assertTrue(cp in avc3)
        self.assertTrue(name not in avc3)

        self.assertEqual(long(el.version.split('.')[-1]),self.revision+2)
        el.close()


    ##  component test
    # \brief It tests default settings
    def test_available_comp_xml(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = self.openConfig(self.__args)
 
        avc = el.availableComponents()
        self.assertTrue(isinstance(avc, list))
        name = "mcs_test_component"
        xml = "<?xml version='1.0'?><definition><group type='NXentry'/></definition>"
        while name in avc:
            name = name + '_1'
#        print avc
        cpx = el.components(avc)
        self.setXML(el, xml)
        self.assertEqual(el.storeComponent(name), None)
        self.__cmps.append(name)
        avc2 = el.availableComponents()
#        print avc2
        cpx2 = el.components(avc2)
        self.assertTrue(isinstance(avc2, list))
        for i in range(len(avc)):
            self.assertTrue(avc[i] in avc2)
            j = avc2.index(avc[i])
            self.assertEqual(cpx2[j], cpx[i])
            
        self.assertTrue(name in avc2)
        j = avc2.index(name)
        self.assertEqual(cpx2[j], xml)
        
        self.assertEqual(el.deleteComponent(name),None)
        self.__cmps.pop()
        
        avc3 = el.availableComponents()
        cpx3 = el.components(avc3)
        self.assertTrue(isinstance(avc3, list))


        for i in range(len(avc)):
            self.assertTrue(avc[i] in avc3)
            j = avc3.index(avc[i])
            self.assertEqual(cpx3[j], cpx[i])
            
        self.assertTrue(name not in avc3)
        
        self.assertEqual(long(el.version.split('.')[-1]),self.revision+2)
        self.assertEqual(el.close(),None)


    ##  component test
    # \brief It tests default settings
    def test_available_no_comp(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = self.openConfig(self.__args)

        avc = el.availableComponents()
        self.assertTrue(isinstance(avc, list))
        name = "mcs_test_component"
        xml = "<?xml version='1.0'?><definition><group type='NXentry'/></definition>"
        while name in avc:
            name = name + '_1'
#        print avc
        self.myAssertRaise(NonregisteredDBRecordError,el.components, [name])
        
        self.assertEqual(long(el.version.split('.')[-1]),self.revision)
        self.assertEqual(el.close(),None)




    ##  component test
    # \brief It tests default settings
    def test_available_comp_update(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = self.openConfig(self.__args)

        avc = el.availableComponents()
        self.assertTrue(isinstance(avc, list))
        name = "mcs_test_component"
        xml = "<?xml version='1.0'?><definition><group type='NXentry'/></definition>"
        xml2 = "<?xml version='1.0'?><definition><group type='NXentry2'/></definition>"
        while name in avc:
            name = name + '_1'
#        print avc
        cpx = el.components(avc)

        self.setXML(el, xml)
        self.assertEqual(el.storeComponent(name),None)
        self.__cmps.append(name)
        avc2 = el.availableComponents()
#        print avc2
        cpx2 = el.components(avc2)
        self.assertTrue(isinstance(avc2, list))
        for i in range(len(avc)):
            self.assertTrue(avc[i] in avc2)
            j = avc2.index(avc[i])
            self.assertEqual(cpx2[j], cpx[i])
            
        self.assertTrue(name in avc2)
        j = avc2.index(name)
        self.assertEqual(cpx2[j], xml)



        self.setXML(el, xml2)
        self.assertEqual(el.storeComponent(name),None)
        self.__cmps.append(name)
        avc2 = el.availableComponents()
#        print avc2
        cpx2 = el.components(avc2)
        self.assertTrue(isinstance(avc2, list))
        for i in range(len(avc)):
            self.assertTrue(avc[i] in avc2)
            j = avc2.index(avc[i])
            self.assertEqual(cpx2[j], cpx[i])
            
        self.assertTrue(name in avc2)
        j = avc2.index(name)
        self.assertEqual(cpx2[j], xml2)

        
        self.assertEqual(el.deleteComponent(name), None)
        self.__cmps.pop()
        
        avc3 = el.availableComponents()
        cpx3 = el.components(avc3)
        self.assertTrue(isinstance(avc3, list))


        for i in range(len(avc)):
            self.assertTrue(avc[i] in avc3)
            j = avc3.index(avc[i])
            self.assertEqual(cpx3[j], cpx[i])
            
        self.assertTrue(name not in avc3)
        
        self.assertEqual(long(el.version.split('.')[-1]),self.revision+3)
        self.assertEqual(el.close(),None)





    ##  component test
    # \brief It tests default settings
    def test_available_comp2_xml(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = self.openConfig(self.__args)

        avc = el.availableComponents()
        self.assertTrue(isinstance(avc, list))
        name = "mcs_test_component"
        xml = "<?xml version='1.0'?><definition><group type='NXentry'/></definition>"
        xml2 = "<?xml version='1.0'?><definition><group type='NXentry2'/></definition>"
        while name in avc:
            name = name + '_1'
        name2 = name + '_2'
        while name2 in avc:
            name2 = name2 + '_2'
#        print avc
        cpx = el.components(avc)

        self.setXML(el, xml)
        self.assertEqual(el.storeComponent(name),None)
        self.__cmps.append(name)
        avc2 = el.availableComponents()
#        print avc2
        cpx2 = el.components(avc2)
        self.assertTrue(isinstance(avc2, list))
        for i in range(len(avc)):
            self.assertTrue(avc[i] in avc2)
            j = avc2.index(avc[i])
            self.assertEqual(cpx2[j], cpx[i])
            
        self.assertTrue(name in avc2)
        j = avc2.index(name)
        self.assertEqual(cpx2[j], xml)


        self.setXML(el, xml2)
        self.assertEqual(el.storeComponent(name2),None)
        self.__cmps.append(name2)
        avc2 = el.availableComponents()
#        print avc2
        cpx2 = el.components(avc2)
        self.assertTrue(isinstance(avc2, list))
        for i in range(len(avc)):
            self.assertTrue(avc[i] in avc2)
            j = avc2.index(avc[i])
            self.assertEqual(cpx2[j], cpx[i])
            
        self.assertTrue(name2 in avc2)
        j = avc2.index(name2)
        self.assertEqual(cpx2[j], xml2)

        cpx2b = el.components([name,name2])
        self.assertEqual(cpx2b[0], xml)
        self.assertEqual(cpx2b[1], xml2)

        
        self.assertEqual(el.deleteComponent(name),None)
        self.__cmps.pop(-2)

        self.assertEqual(el.deleteComponent(name2),None)
        self.__cmps.pop()
        
        avc3 = el.availableComponents()
        cpx3 = el.components(avc3)
        self.assertTrue(isinstance(avc3, list))


        for i in range(len(avc)):
            self.assertTrue(avc[i] in avc3)
            j = avc3.index(avc[i])
            self.assertEqual(cpx3[j], cpx[i])
            
        self.assertTrue(name not in avc3)
        
        self.assertEqual(long(el.version.split('.')[-1]),self.revision+4)
        self.assertEqual(el.close(),None)









    ## comp_available test
    # \brief It tests XMLConfigurator
    def test_dsrc_available(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        avc = el.availableDataSources()

        self.assertTrue(isinstance(avc, list))
        name = "mcs_test_datasource"
        xml = "<?xml version='1.0'?><definition><group type='NXentry'/></definition>"
        while name in avc:
            name = name + '_1'
#        print avc
        self.setXML(el, xml)
        self.assertEqual(el.storeDataSource(name),None)
        self.assertEqual(el.storeDataSource(name),None)
        self.__ds.append(name)
        avc2 = el.availableDataSources()
#        print avc2
        self.assertTrue(isinstance(avc2, list))
        for cp in avc:
            self.assertTrue(cp in avc2)
            
        self.assertTrue(name in avc2)
        cpx = el.dataSources([name])
        self.assertEqual(cpx[0], xml)
        
        self.assertEqual(el.deleteDataSource(name),None)
        self.__ds.pop()
        
        avc3 = el.availableDataSources()
        self.assertTrue(isinstance(avc3, list))
        for cp in avc:
            self.assertTrue(cp in avc3)
        self.assertTrue(name not in avc3)

        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 2 )
        el.close()


    ##  dataSource test
    # \brief It tests default settings
    def test_available_dsrc_xml(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = self.openConfig(self.__args)
 
        avc = el.availableDataSources()
        self.assertTrue(isinstance(avc, list))
        name = "mcs_test_datasource"
        xml = "<?xml version='1.0'?><definition><group type='NXentry'/></definition>"
        while name in avc:
            name = name + '_1'
#        print avc
        cpx = el.dataSources(avc)
        self.setXML(el, xml)
        self.assertEqual(el.storeDataSource(name), None)
        self.__ds.append(name)
        avc2 = el.availableDataSources()
#        print avc2
        cpx2 = el.dataSources(avc2)
        self.assertTrue(isinstance(avc2, list))
        for i in range(len(avc)):
            self.assertTrue(avc[i] in avc2)
            j = avc2.index(avc[i])
            self.assertEqual(cpx2[j], cpx[i])
            
        self.assertTrue(name in avc2)
        j = avc2.index(name)
        self.assertEqual(cpx2[j], xml)
        
        self.assertEqual(el.deleteDataSource(name),None)
        self.__ds.pop()
        
        avc3 = el.availableDataSources()
        cpx3 = el.dataSources(avc3)
        self.assertTrue(isinstance(avc3, list))


        for i in range(len(avc)):
            self.assertTrue(avc[i] in avc3)
            j = avc3.index(avc[i])
            self.assertEqual(cpx3[j], cpx[i])
            
        self.assertTrue(name not in avc3)
        
        self.assertEqual(long(el.version.split('.')[-1]),self.revision+2)
        self.assertEqual(el.close(),None)


    ##  dataSource test
    # \brief It tests default settings
    def test_available_no_dsrc(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = self.openConfig(self.__args)

        avc = el.availableDataSources()
        self.assertTrue(isinstance(avc, list))
        name = "mcs_test_datasource"
        xml = "<?xml version='1.0'?><definition><group type='NXentry'/></definition>"
        while name in avc:
            name = name + '_1'
#        print avc
        self.myAssertRaise(NonregisteredDBRecordError,el.dataSources, [name])
        
        self.assertEqual(long(el.version.split('.')[-1]),self.revision)
        self.assertEqual(el.close(),None)




    ##  dataSource test
    # \brief It tests default settings
    def test_available_dsrc_update(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = self.openConfig(self.__args)

        avc = el.availableDataSources()
        self.assertTrue(isinstance(avc, list))
        name = "mcs_test_datasource"
        xml = "<?xml version='1.0'?><definition><group type='NXentry'/></definition>"
        xml2 = "<?xml version='1.0'?><definition><group type='NXentry2'/></definition>"
        while name in avc:
            name = name + '_1'
#        print avc
        cpx = el.dataSources(avc)

        self.setXML(el, xml)
        self.assertEqual(el.storeDataSource(name),None)
        self.__ds.append(name)
        avc2 = el.availableDataSources()
#        print avc2
        cpx2 = el.dataSources(avc2)
        self.assertTrue(isinstance(avc2, list))
        for i in range(len(avc)):
            self.assertTrue(avc[i] in avc2)
            j = avc2.index(avc[i])
            self.assertEqual(cpx2[j], cpx[i])
            
        self.assertTrue(name in avc2)
        j = avc2.index(name)
        self.assertEqual(cpx2[j], xml)



        self.setXML(el, xml2)
        self.assertEqual(el.storeDataSource(name),None)
        self.__ds.append(name)
        avc2 = el.availableDataSources()
#        print avc2
        cpx2 = el.dataSources(avc2)
        self.assertTrue(isinstance(avc2, list))
        for i in range(len(avc)):
            self.assertTrue(avc[i] in avc2)
            j = avc2.index(avc[i])
            self.assertEqual(cpx2[j], cpx[i])
            
        self.assertTrue(name in avc2)
        j = avc2.index(name)
        self.assertEqual(cpx2[j], xml2)

        
        self.assertEqual(el.deleteDataSource(name), None)
        self.__ds.pop()
        
        avc3 = el.availableDataSources()
        cpx3 = el.dataSources(avc3)
        self.assertTrue(isinstance(avc3, list))


        for i in range(len(avc)):
            self.assertTrue(avc[i] in avc3)
            j = avc3.index(avc[i])
            self.assertEqual(cpx3[j], cpx[i])
            
        self.assertTrue(name not in avc3)
        
        self.assertEqual(long(el.version.split('.')[-1]),self.revision+3)
        self.assertEqual(el.close(),None)





    ##  dataSource test
    # \brief It tests default settings
    def test_available_dsrc2_xml(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = self.openConfig(self.__args)

        avc = el.availableDataSources()
        self.assertTrue(isinstance(avc, list))
        name = "mcs_test_datasource"
        xml = "<?xml version='1.0'?><definition><group type='NXentry'/></definition>"
        xml2 = "<?xml version='1.0'?><definition><group type='NXentry2'/></definition>"
        while name in avc:
            name = name + '_1'
        name2 = name + '_2'
        while name2 in avc:
            name2 = name2 + '_2'
#        print avc
        cpx = el.dataSources(avc)

        self.setXML(el, xml)
        self.assertEqual(el.storeDataSource(name),None)
        self.__ds.append(name)
        avc2 = el.availableDataSources()
#        print avc2
        cpx2 = el.dataSources(avc2)
        self.assertTrue(isinstance(avc2, list))
        for i in range(len(avc)):
            self.assertTrue(avc[i] in avc2)
            j = avc2.index(avc[i])
            self.assertEqual(cpx2[j], cpx[i])
            
        self.assertTrue(name in avc2)
        j = avc2.index(name)
        self.assertEqual(cpx2[j], xml)


        self.setXML(el, xml2)
        self.assertEqual(el.storeDataSource(name2),None)
        self.__ds.append(name2)
        avc2 = el.availableDataSources()
#        print avc2
        cpx2 = el.dataSources(avc2)
        self.assertTrue(isinstance(avc2, list))
        for i in range(len(avc)):
            self.assertTrue(avc[i] in avc2)
            j = avc2.index(avc[i])
            self.assertEqual(cpx2[j], cpx[i])
            
        self.assertTrue(name2 in avc2)
        j = avc2.index(name2)
        self.assertEqual(cpx2[j], xml2)

        cpx2b = el.dataSources([name,name2])
        self.assertEqual(cpx2b[0], xml)
        self.assertEqual(cpx2b[1], xml2)

        
        self.assertEqual(el.deleteDataSource(name),None)
        self.__ds.pop(-2)

        self.assertEqual(el.deleteDataSource(name2),None)
        self.__ds.pop()
        
        avc3 = el.availableDataSources()
        cpx3 = el.dataSources(avc3)
        self.assertTrue(isinstance(avc3, list))


        for i in range(len(avc)):
            self.assertTrue(avc[i] in avc3)
            j = avc3.index(avc[i])
            self.assertEqual(cpx3[j], cpx[i])
            
        self.assertTrue(name not in avc3)
        
        self.assertEqual(long(el.version.split('.')[-1]),self.revision+4)
        self.assertEqual(el.close(),None)






    ##  component test
    # \brief It tests default settings
    def test_mandatory_no_comp(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        self.assertTrue(isinstance(man, list))
        avc = el.availableComponents()
        
        name = "mcs_test_component"
        xml = "<?xml version='1.0'?><definition><group type='NXentry'/></definition>"
        while name in avc:
            name = name + '_1'
#        print avc

        self.assertEqual(el.setMandatoryComponents([name]), None)
        man2 = el.mandatoryComponents()
#        for cp in man:
#            self.assertTrue(cp in man2)
            
        #        self.assertTrue(name in man2)
        self.assertEqual(len(man),len(man2))
        for cp in man:
            self.assertTrue(cp in man2)
            

        self.assertEqual(el.close(),None)



    ##  component test
    # \brief It tests default settings
    def test_mandatory_comp(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        self.assertTrue(isinstance(man, list))
        avc = el.availableComponents()
        
        name = "mcs_test_component"
        xml = "<?xml version='1.0'?><definition><group type='NXentry'/></definition>"
        while name in avc:
            name = name + '_1'
#        print avc
        self.setXML(el, xml)
        self.assertEqual(el.storeComponent(name),None)
        self.__cmps.append(name)

#        print man
        self.assertEqual(el.setMandatoryComponents([name]), None)
        self.assertEqual(el.setMandatoryComponents([name]), None)
        man2 = el.mandatoryComponents()
        self.assertEqual(len(man)+1,len(man2))
        for cp in man:
            self.assertTrue(cp in man2)
            
        self.assertTrue(name in man2)

        self.assertEqual(el.unsetMandatoryComponents([name]), None)
        self.assertEqual(el.unsetMandatoryComponents([name]), None)

        man2 = el.mandatoryComponents()
        self.assertEqual(len(man),len(man2))
        for cp in man:
            self.assertTrue(cp in man2)
            
        self.assertTrue(not name in man2)

        self.assertEqual(el.deleteComponent(name), None)
        self.__cmps.pop()

        man2 = el.mandatoryComponents()
        self.assertEqual(len(man),len(man2))
        for cp in man:
            self.assertTrue(cp in man2)
            
        self.assertTrue(not name in man2)
            

        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 4)
        self.assertEqual(el.close(), None)



    ##  component test
    # \brief It tests default settings
    def test_mandatory_comp2(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        self.assertTrue(isinstance(man, list))
        avc = el.availableComponents()
        
        name = "mcs_test_component"
        xml = "<?xml version='1.0'?><definition><group type='NXentry'/></definition>"
        while name in avc:
            name = name + '_1'
            
        name2 = name + '_2'
        while name2 in avc:
            name2 = name2 + '_2'
#        print avc


        self.setXML(el, xml)
        self.assertEqual(el.storeComponent(name),None)
        self.__cmps.append(name)

#        print man
        self.assertEqual(el.setMandatoryComponents([name]), None)
        man2 = el.mandatoryComponents()
        self.assertEqual(len(man)+1,len(man2))
        for cp in man:
            self.assertTrue(cp in man2)
            
        self.assertTrue(name in man2)

        self.setXML(el, xml)
        self.assertEqual(el.storeComponent(name2),None)
        self.__cmps.append(name2)

#        print man
        self.assertEqual(el.setMandatoryComponents([name2]), None)
        man2 = el.mandatoryComponents()
        self.assertEqual(len(man)+2,len(man2))
        for cp in man:
            self.assertTrue(cp in man2)
            
        self.assertTrue(name in man2)
        self.assertTrue(name2 in man2)

        self.assertEqual(el.unsetMandatoryComponents([name]), None)


#        print man
        man2 = el.mandatoryComponents()
        self.assertEqual(len(man)+1,len(man2))
        for cp in man:
            self.assertTrue(cp in man2)
            
        self.assertTrue(name2 in man2)


        self.assertEqual(el.unsetMandatoryComponents([name2]), None)

        man2 = el.mandatoryComponents()
        self.assertEqual(len(man),len(man2))
        for cp in man:
            self.assertTrue(cp in man2)
            
        self.assertTrue(not name in man2)

        self.assertEqual(el.deleteComponent(name), None)
        self.__cmps.pop()
        self.assertEqual(el.deleteComponent(name2), None)
        self.__cmps.pop()

        man2 = el.mandatoryComponents()
        self.assertEqual(len(man),len(man2))
        for cp in man:
            self.assertTrue(cp in man2)
            
        self.assertTrue(not name in man2)
            

        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 8 )
        self.assertEqual(el.close(), None)






    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_default(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)

        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man

        xml = self.getXML(el)
        self.assertEqual(self.getXML(el), '')
        self.assertEqual(el.createConfiguration([]), None)
        xml = self.getXML(el)
        self.assertEqual(self.getXML(el), '')
        el.setMandatoryComponents(man)
        el.close()


    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_default_2(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()

        self.assertTrue(isinstance(avc, list))
        name = "mcs_test_component"
        xml = "<?xml version='1.0'?><definition><group type='NXentry'/></definition>"
        while name in avc:
            name = name + '_1'
#        print avc
        self.setXML(el, xml)
        self.assertEqual(el.storeComponent(name),None)
        self.__cmps.append(name)
        avc2 = el.availableComponents()
#        print avc2
        self.assertTrue(isinstance(avc2, list))
        for cp in avc:
            self.assertTrue(cp in avc2)
            
        self.assertTrue(name in avc2)


        cpx = el.components([name])
        self.assertEqual(cpx[0], xml)
        
        self.assertEqual(el.createConfiguration([name]), None)
        xml = self.getXML(el)
        self.assertEqual(
            xml.replace("?>\n<","?><"),
            '<?xml version="1.0" ?><definition> <group type="NXentry"/></definition>')

        self.assertEqual(el.deleteComponent(name),None)
        self.__cmps.pop()
        
        avc3 = el.availableComponents()
        self.assertTrue(isinstance(avc3, list))
        for cp in avc:
            self.assertTrue(cp in avc3)
        self.assertTrue(name not in avc3)


        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 2)
        el.close()







    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_default_2_var(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()

        self.assertTrue(isinstance(avc, list))
        name = "mcs_test_component"
        xml = "<?xml version='1.0'?><definition><group type='NXentry' name='$var.myentry'/></definition>"
        while name in avc:
            name = name + '_1'
#        print avc
        self.setXML(el, xml)
        self.assertEqual(el.storeComponent(name),None)
        self.__cmps.append(name)
        avc2 = el.availableComponents()
#        print avc2
        self.assertTrue(isinstance(avc2, list))
        for cp in avc:
            self.assertTrue(cp in avc2)
            
        self.assertTrue(name in avc2)


        cpx = el.components([name])
        self.assertEqual(cpx[0], xml)
        
        
        self.assertEqual(el.createConfiguration([name]), None)
        xml = self.getXML(el)
        self.assertEqual(
            xml.replace("?>\n<","?><"),
            '<?xml version="1.0" ?><definition> <group name="" type="NXentry"/></definition>')

        el.variables = '{"myentry":"entry1"}'
        self.assertEqual(el.createConfiguration([name]), None)

        
        xml = self.getXML(el)
        self.assertEqual(
            xml.replace("?>\n<","?><"),
            '<?xml version="1.0" ?><definition> <group name="entry1" type="NXentry"/></definition>')

        self.assertEqual(el.deleteComponent(name),None)
        self.__cmps.pop()
        
        avc3 = el.availableComponents()
        self.assertTrue(isinstance(avc3, list))
        for cp in avc:
            self.assertTrue(cp in avc3)
        self.assertTrue(name not in avc3)


        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 2)
        el.close()



    # \brief It tests XMLConfigurator
    def test_createConf_default_2_var2(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()

        self.assertTrue(isinstance(avc, list))
        name = "mcs_test_component"
        xml = "<?xml version='1.0'?><definition><group type='$var.entryType' name='$var.myentry'/></definition>"
        while name in avc:
            name = name + '_1'
#        print avc
        self.setXML(el, xml)
        self.assertEqual(el.storeComponent(name),None)
        self.__cmps.append(name)
        avc2 = el.availableComponents()
#        print avc2
        self.assertTrue(isinstance(avc2, list))
        for cp in avc:
            self.assertTrue(cp in avc2)
            
        self.assertTrue(name in avc2)


        cpx = el.components([name])
        self.assertEqual(cpx[0], xml)
        
        self.assertEqual(el.createConfiguration([name]), None)

        
        xml = self.getXML(el)
        self.assertEqual(
            xml.replace("?>\n<","?><"),
            '<?xml version="1.0" ?><definition> <group name="" type=""/></definition>')
        el.variables = '{"myentry":"entry1", "entryType":"NXentry"}'
        self.assertEqual(el.createConfiguration([name]), None)

        
        xml = self.getXML(el)
        self.assertEqual(
            xml.replace("?>\n<","?><"),
            '<?xml version="1.0" ?><definition> <group name="entry1" type="NXentry"/></definition>')

        self.assertEqual(el.deleteComponent(name),None)
        self.__cmps.pop()
        
        avc3 = el.availableComponents()
        self.assertTrue(isinstance(avc3, list))
        for cp in avc:
            self.assertTrue(cp in avc3)
        self.assertTrue(name not in avc3)


        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 2)
        el.close()






    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_def(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()

        self.assertTrue(isinstance(avc, list))
        name = "mcs_test_component"
        xml = "<group type='NXentry'/>"
        while name in avc:
            name = name + '_1'
#        print avc
        self.setXML(el, xml)
        self.assertEqual(el.storeComponent(name),None)
        self.__cmps.append(name)
        avc2 = el.availableComponents()
#        print avc2
        self.assertTrue(isinstance(avc2, list))
        for cp in avc:
            self.assertTrue(cp in avc2)
            
        self.assertTrue(name in avc2)


        cpx = el.components([name])
        self.assertEqual(cpx[0], xml)
        
        self.myAssertRaise(UndefinedTagError,el.createConfiguration,[name])

        self.assertEqual(el.deleteComponent(name),None)
        self.__cmps.pop()
        
        avc3 = el.availableComponents()
        self.assertTrue(isinstance(avc3, list))
        for cp in avc:
            self.assertTrue(cp in avc3)
        self.assertTrue(name not in avc3)


        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 2)
        el.close()



    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_group(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man

        avc = el.availableComponents()

        self.assertTrue(isinstance(avc, list))
        name = ["mcs_test_component"]
        xml = ["<definition/>", "<definition><group type='NXentry'/></definition>"]
        name.append(name[0] +'_2')
        while name[0] in avc:
            name[0] = name[0] + '_1'
        while name[1] in avc:
            name[1] = name[1] + '_2'
#        print avc
        self.setXML(el, xml[0])    
        self.assertEqual(el.storeComponent(name[0]),None)
        self.__cmps.append(name[0])

        self.setXML(el, xml[1])    
        self.assertEqual(el.storeComponent(name[1]),None)
        self.__cmps.append(name[1])

        
        self.assertEqual(el.createConfiguration(name), None)
        gxml = self.getXML(el)
        self.assertEqual(gxml.replace("?>\n<","?><"),
                         '<?xml version="1.0" ?><definition> <group type="NXentry"/></definition>')

        self.assertEqual(el.deleteComponent(name[1]),None)
        self.__cmps.pop()

        self.assertEqual(el.deleteComponent(name[0]),None)
        self.__cmps.pop()
        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 4)
        el.close()






    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_group_5(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man

        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = [ "<definition><group type='NXentry'/></definition>"]*5
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        self.assertEqual(el.createConfiguration(name), None)
        gxml = self.getXML(el)
        self.assertEqual(gxml.replace("?>\n<","?><"),'<?xml version="1.0" ?><definition> <group type="NXentry"/></definition>')

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 10)
        el.close()





    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_group_group(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ["<definition><group type='NXentry'/></definition>","<definition><group type='NXentry2'/></definition>"]
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        self.assertEqual(el.createConfiguration(name), None)
        gxml = self.getXML(el)
        self.assertTrue((gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition> <group type="NXentry2"/> <group type="NXentry"/></definition>') | 
                        (gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition> <group type="NXentry"/> <group type="NXentry2"/></definition>'))

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 4)
        el.close()



    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_group_group_error(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man

        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ["<definition><group type='NXentry'/></definition>","<group/>"]
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        self.myAssertRaise(UndefinedTagError,el.createConfiguration, name)

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        el.close()



    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_group_group_error_2(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man

        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ["<group/>","<definition><group type='NXentry'/></definition>"]
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        self.myAssertRaise(UndefinedTagError,el.createConfiguration, name)

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 4)
        el.close()





    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_group_field_3(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man

        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ["<definition><group type='NXentry'><field type='field'/></group></definition>"]*3
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        self.assertEqual(el.createConfiguration(name), None)
        gxml = self.getXML(el)
        self.assertEqual(gxml.replace("?>\n<","?><"),'<?xml version="1.0" ?><definition> <group type="NXentry">  <field type="field"/> </group></definition>')

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 6)
        el.close()



    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_group_group_field(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man

        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ["<definition><group type='NXentry'><field name='field1'/></group></definition>","<definition><group type='NXentry2'/><field name='field1'/></definition>"]
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        self.assertEqual(el.createConfiguration(name), None)
        gxml = self.getXML(el)
        self.assertTrue((gxml.replace("?>\n<","?><") =='<?xml version="1.0" ?><definition> <group type="NXentry2"/> <field name="field1"/> <group type="NXentry">  <field name="field1"/> </group></definition>' ) |
                        (gxml.replace("?>\n<","?><") =='<?xml version="1.0" ?><definition> <group type="NXentry">  <field name="field1"/> </group> <group type="NXentry2"/> <field name="field1"/></definition>' ))

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 4)
        el.close()





    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_group_group_2(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ["<definition><group name='entry'/></definition>","<definition><group type='NXentry2'/></definition>"]
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        self.assertEqual(el.createConfiguration(name), None)
        gxml = self.getXML(el)
        self.assertEqual(gxml.replace("?>\n<","?><"),'<?xml version="1.0" ?><definition> <group name="entry" type="NXentry2"/></definition>')

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 4)
        el.close()




    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_group_group_3(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ["<definition><group name='entry'/></definition>","<definition><group name='entry' type='NXentry'/></definition>"]
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        self.assertEqual(el.createConfiguration(name), None)
        gxml = self.getXML(el)
        self.assertTrue((gxml.replace("?>\n<","?><") =='<?xml version="1.0" ?><definition> <group name="entry" type="NXentry"/></definition>'))

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 4)
        el.close()




    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_group_group_4(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ["<definition><group name='entry2'/></definition>","<definition><group name='entry' type='NXentry'/></definition>"]
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        self.assertEqual(el.createConfiguration(name), None)
        gxml = self.getXML(el)
        self.assertTrue((gxml.replace("?>\n<","?><")== '<?xml version="1.0" ?><definition> <group name="entry" type="NXentry"/> <group name="entry2"/></definition>') |
                        (gxml.replace("?>\n<","?><") =='<?xml version="1.0" ?><definition> <group name="entry2"/> <group name="entry" type="NXentry"/></definition>'))

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 4)
        el.close()



    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_group_field_4(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man

        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ["<definition><group type='NXentry'><field type='field'/></group></definition>"]*15
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        self.assertEqual(el.createConfiguration(name), None)
        gxml = self.getXML(el)
        self.assertEqual(gxml.replace("?>\n<","?><"), '<?xml version="1.0" ?><definition> <group type="NXentry">  <field type="field"/> </group></definition>')

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 30)
        el.close()




    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_group_field_5(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man

        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ["<definition><group  name='entry' type='NXentry'><field type='field'/></group></definition>","<definition><group name='entry' type='NXentry'><field type='field'/></group></definition>"]
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        self.assertEqual(el.createConfiguration(name), None)
        gxml = self.getXML(el)
        self.assertEqual(gxml.replace("?>\n<","?><"), '<?xml version="1.0" ?><definition> <group name="entry" type="NXentry">  <field type="field"/> </group></definition>' )

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 4 )
        el.close()




    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_group_field_var(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man

        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ["<definition><group  name='$var.entry' type='NXentry'><field type='field'/></group></definition>","<definition><group name='$var.entry' type='NXentry'><field type='field'>$var.value</field></group></definition>"]
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        el.variables = '{"entry":"entry", "value":"myvalue", "some":"ble"}'
        self.assertEqual(el.createConfiguration(name), None)
        gxml = self.getXML(el)
        self.assertEqual(gxml.replace("> ", ">").replace(">  ", ">").replace(">   ", ">").replace(" <", "<").replace("  <", "<").replace("   <", "<").replace("?>\n<","?><").replace(" <", "<"), 
                         '<?xml version="1.0" ?><definition><group name="entry" type="NXentry"><field type="field">myvalue</field></group></definition>' )

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 4 )
        el.close()




    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_group_field_name_error(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man

        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ["<definition><group  name='entry' type='NXentry'><field type='field'/></group></definition>","<definition><group name='entry' type='NXentry2'><field type='field'/></group></definition>"]
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        self.myAssertRaise(IncompatibleNodeError,el.createConfiguration, name)
         
        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 4)
        el.close()



    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_single_name(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man

        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ["<definition><group  name='entry' type='NXentry'><field type='field'/></group></definition>","<definition><group name='entry2' type='NXentry2'><field type='field'/></group></definition>"]
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        self.assertEqual(el.createConfiguration(name), None)
        gxml = self.getXML(el)
        self.assertTrue((gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition> <group name="entry2" type="NXentry2">  <field type="field"/> </group> <group name="entry" type="NXentry">  <field type="field"/> </group></definition>' ) |
                        (gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition> <group name="entry" type="NXentry">  <field type="field"/> </group> <group name="entry2" type="NXentry2">  <field type="field"/> </group></definition>' ) )

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 4)
        el.close()



    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_single_name_2_error(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        mr = Merger()
        for sg in mr.singles:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><group  name='entry' type='NXentry'><%s name='field2'/></group></definition>" % sg,"<definition><group name='entry2' type='NXentry2'><%s name='field'/></group></definition>" % sg]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])

        
            self.myAssertRaise(IncompatibleNodeError,el.createConfiguration,name)


            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 4)
        el.close()



    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_uniqueText_error(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        mr = Merger()
        for ut in mr.uniqueText:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><group  name='entry' type='NXentry'><%s type='field'>My text </%s></group></definition>" %(ut ,ut),"<definition><group  name='entry' type='NXentry'><%s type='field'>My text 2 </%s></group></definition>" %(ut ,ut)]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])

        
            self.myAssertRaise(IncompatibleNodeError,el.createConfiguration,name)

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 4)
        el.close()






    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_children_datasource(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = Merger()
        uts = self.children
        for ut in uts:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><field  name='entry' ><datasource type='TANGO'><%s/></datasource></field></definition>" % ut ]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            self.assertEqual(el.createConfiguration(name), None)
            gxml = self.getXML(el)
            self.assertEqual(gxml.replace("?>\n<","?><"),  '<?xml version="1.0" ?><definition> <field name="entry">  <datasource type="TANGO">   <%s/>  </datasource> </field></definition>' % (ut) )

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision+2)
        el.close()





    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_children_datasource_error(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = Merger()
        uts = []
        for k in el.children:
            for w in el.children[k]:
                if w not in  self.children:
                    uts.append(w)

        uts = set(uts)

        for ut in uts:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><field  name='entry' ><datasource type='TANGO'><%s/></datasource></field></definition>" % ut ]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])

            el.createConfiguration(name)

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision+2)
        el.close()




    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_children_attribute(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = Merger()
        uts = el.children['attribute']
        for ut in uts:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><field  name='entry' ><attribute type='TANGO'><%s/></attribute></field></definition>" % ut ]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            self.assertEqual(el.createConfiguration(name), None)
            gxml = self.getXML(el)
            self.assertEqual(gxml.replace("?>\n<","?><"),  '<?xml version="1.0" ?><definition> <field name="entry">  <attribute type="TANGO">   <%s/>  </attribute> </field></definition>' % (ut) )

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision+2)
        el.close()





    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_children_attribute_error(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = Merger()
        uts = []
        for k in el.children:
            for w in el.children[k]:
                if w not in  el.children["attribute"]:
                    uts.append(w)
        uts = set(uts)
        for ut in uts:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><field  name='entry' ><attribute type='TANGO'><%s/></attribute></field></definition>" % ut ]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            self.myAssertRaise(IncompatibleNodeError,el.createConfiguration, name)

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision+2)
        el.close()




    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_children_definition(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = Merger()
        uts = el.children['definition']
        for ut in uts:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><%s  name='entry' /></definition>" % ut ]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            self.assertEqual(el.createConfiguration(name), None)
            gxml = self.getXML(el)
            self.assertEqual(gxml.replace("?>\n<","?><"),  '<?xml version="1.0" ?><definition> <%s name="entry"/></definition>' % (ut) )

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision+2)
        el.close()




    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_children_definition_error(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = Merger()
        uts = []
        for k in el.children:
            for w in el.children[k]:
                if w not in  el.children["definition"]:
                    uts.append(w)

        uts = set(uts)

        for ut in uts:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><%s  name='entry' /></definition>" % ut ]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            self.myAssertRaise(IncompatibleNodeError,el.createConfiguration, name)

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision+2)
        el.close()






    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_children_dimensions(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = Merger()
        uts = el.children['dimensions']
        for ut in uts:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><field  name='entry' ><dimensions type='TANGO'><%s/></dimensions></field></definition>" % ut  ]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            self.assertEqual(el.createConfiguration(name), None)
            gxml = self.getXML(el)
            self.assertEqual(gxml.replace("?>\n<","?><"),'<?xml version="1.0" ?><definition> <field name="entry">  <dimensions type="TANGO">   <%s/>  </dimensions> </field></definition>' % (ut) )

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision+2 )
        el.close()



    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_children_dimensions_error(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = Merger()
        uts = []
        for k in el.children:
            for w in el.children[k]:
                if w not in  el.children["dimensions"]:
                    uts.append(w)

        uts = set(uts)
        for ut in uts:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><field  name='entry' ><dimensions type='TANGO'><%s/></dimensions></field></definition>" % ut  ]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            self.myAssertRaise(IncompatibleNodeError,el.createConfiguration,name)

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision +2)
        el.close()



    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_children_field(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = Merger()
        uts = el.children['field']
        for ut in uts:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><field  name='entry' ><%s/></field></definition>" % ut  ]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            self.assertEqual(el.createConfiguration(name), None)
            gxml = self.getXML(el)
            self.assertEqual(gxml.replace("?>\n<","?><"),'<?xml version="1.0" ?><definition> <field name="entry">  <%s/> </field></definition>' % (ut) )

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision +2 )
        el.close()


    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_children_field_error(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = Merger()
        uts = []
        for k in el.children:
            for w in el.children[k]:
                if w not in  el.children["field"]:
                    uts.append(w)

        uts = set(uts)
        for ut in uts:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><field  name='entry' ><%s/></field></definition>" % ut  ]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            self.myAssertRaise(IncompatibleNodeError,el.createConfiguration,name)

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision +2)
        el.close()


    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_children_group(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = Merger()
        uts = el.children['group']
        for ut in uts:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><group  name='entry' ><%s/></group></definition>" % ut  ]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            self.assertEqual(el.createConfiguration(name), None)
            gxml = self.getXML(el)
            self.assertEqual(gxml.replace("?>\n<","?><"),'<?xml version="1.0" ?><definition> <group name="entry">  <%s/> </group></definition>' % (ut) )

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 2)
        el.close()


    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_children_group_error(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = Merger()
        uts = []
        for k in el.children:
            for w in el.children[k]:
                if w not in  el.children["group"]:
                    uts.append(w)

        uts = set(uts)
        for ut in uts:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><group  name='entry' ><%s/></group></definition>" % ut  ]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])

            self.myAssertRaise(IncompatibleNodeError,el.createConfiguration,name)


            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 2)
        el.close()





    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_children_link(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = Merger()
        uts = el.children['link']
        for ut in uts:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><link  name='entry' ><%s/></link></definition>" % ut  ]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            self.assertEqual(el.createConfiguration(name), None)
            gxml = self.getXML(el)
            self.assertEqual(gxml.replace("?>\n<","?><"),
                             '<?xml version="1.0" ?><definition> <link name="entry">  <%s/> </link></definition>' % (ut) )

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 2)
        el.close()


    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_children_link_error(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = Merger()
        uts = []
        for k in el.children:
            for w in el.children[k]:
                if w not in  el.children["link"]:
                    uts.append(w)

        uts = set(uts)
        for ut in uts:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><link  name='entry' ><%s/></link></definition>" % ut  ]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            self.myAssertRaise(IncompatibleNodeError,el.createConfiguration,name)

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 2)
        el.close()







    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_group_group_mandatory(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ["<definition><group type='NXentry'/></definition>","<definition><group type='NXentry2'/></definition>"]
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        el.setMandatoryComponents([name[0]])
        self.assertEqual(el.mandatoryComponents(),[name[0]])
        

        self.assertEqual(el.createConfiguration([name[1]]), None)
        gxml = self.getXML(el)
        self.assertTrue((gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition> <group type="NXentry2"/> <group type="NXentry"/></definition>') |
                         (gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition> <group type="NXentry"/> <group type="NXentry2"/></definition>'))

        el.unsetMandatoryComponents([name[0]])
        self.assertEqual(el.mandatoryComponents(),[])

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 6)
        el.close()



    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_group_group_group_mandatory(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ["<definition><group type='NXentry'/></definition>",
               "<definition><group type='NXentry2'/></definition>",
               "<definition><group type='NXentry3'/></definition>"
               ]
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        el.setMandatoryComponents([name[0],name[1]])
        self.assertEqual(el.mandatoryComponents().sort(),[name[0],name[1]].sort())

        
        self.assertEqual(el.createConfiguration([name[2]]), None)
        gxml = self.getXML(el)

        self.assertTrue( 
            (gxml.replace("?>\n<","?><") ==  '<?xml version="1.0" ?><definition> <group type="NXentry2"/> <group type="NXentry3"/> <group type="NXentry"/></definition>') | 
            (gxml.replace("?>\n<","?><") ==  '<?xml version="1.0" ?><definition> <group type="NXentry3"/> <group type="NXentry2"/> <group type="NXentry"/></definition>') |
            (gxml.replace("?>\n<","?><") ==  '<?xml version="1.0" ?><definition> <group type="NXentry3"/> <group type="NXentry"/> <group type="NXentry2"/></definition>') |
            (gxml.replace("?>\n<","?><") ==  '<?xml version="1.0" ?><definition> <group type="NXentry2"/> <group type="NXentry"/> <group type="NXentry3"/></definition>') |
            (gxml.replace("?>\n<","?><") ==  '<?xml version="1.0" ?><definition> <group type="NXentry"/> <group type="NXentry2"/> <group type="NXentry3"/></definition>') |
            (gxml.replace("?>\n<","?><") ==  '<?xml version="1.0" ?><definition> <group type="NXentry"/> <group type="NXentry3"/> <group type="NXentry2"/></definition>') 
                         )
        

        el.unsetMandatoryComponents([name[1]])


        self.assertEqual(el.mandatoryComponents(),[name[0]])

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        self.assertEqual(el.mandatoryComponents(),[])
        

        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 9)
        el.setMandatoryComponents(man)
        el.close()




    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_default(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)

        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man

        xml = self.getXML(el)
        self.assertEqual(self.getXML(el), '')
        xml  = el.merge([])
        self.assertEqual(self.getXML(el), '')
        el.setMandatoryComponents(man)
        el.close()


    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_default_2(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()

        self.assertTrue(isinstance(avc, list))
        name = "mcs_test_component"
        xml = "<?xml version='1.0'?><definition><group type='NXentry'/></definition>"
        while name in avc:
            name = name + '_1'
#        print avc
        self.setXML(el, xml)
        self.assertEqual(el.storeComponent(name),None)
        self.__cmps.append(name)
        avc2 = el.availableComponents()
#        print avc2
        self.assertTrue(isinstance(avc2, list))
        for cp in avc:
            self.assertTrue(cp in avc2)
            
        self.assertTrue(name in avc2)


        cpx = el.components([name])
        self.assertEqual(cpx[0], xml)
        
        xml = el.merge([name])
        self.assertEqual(
            xml.replace("?>\n<","?><"),
            '<?xml version="1.0" ?><definition><group type="NXentry"/></definition>')

        self.assertEqual(el.deleteComponent(name),None)
        self.__cmps.pop()
        
        avc3 = el.availableComponents()
        self.assertTrue(isinstance(avc3, list))
        for cp in avc:
            self.assertTrue(cp in avc3)
        self.assertTrue(name not in avc3)


        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 2)
        el.close()







    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_default_2_var(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()

        self.assertTrue(isinstance(avc, list))
        name = "mcs_test_component"
        xml = "<?xml version='1.0'?><definition><group type='NXentry' name='$var.myentry'/></definition>"
        while name in avc:
            name = name + '_1'
#        print avc
        self.setXML(el, xml)
        self.assertEqual(el.storeComponent(name),None)
        self.__cmps.append(name)
        avc2 = el.availableComponents()
#        print avc2
        self.assertTrue(isinstance(avc2, list))
        for cp in avc:
            self.assertTrue(cp in avc2)
            
        self.assertTrue(name in avc2)


        cpx = el.components([name])
        self.assertEqual(cpx[0], xml)
        
        
        xml = el.merge([name])
        self.assertEqual(
            xml.replace("?>\n<","?><"),
            '<?xml version="1.0" ?><definition><group name="$var.myentry" type="NXentry"/></definition>')

        el.variables = '{"myentry":"entry1"}'
        xml = el.merge([name])

        
        self.assertEqual(
            xml.replace("?>\n<","?><"),
            '<?xml version="1.0" ?><definition><group name="$var.myentry" type="NXentry"/></definition>')

        self.assertEqual(el.deleteComponent(name),None)
        self.__cmps.pop()
        
        avc3 = el.availableComponents()
        self.assertTrue(isinstance(avc3, list))
        for cp in avc:
            self.assertTrue(cp in avc3)
        self.assertTrue(name not in avc3)


        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 2)
        el.close()



    # \brief It tests XMLConfigurator
    def test_merge_default_2_var2(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()

        self.assertTrue(isinstance(avc, list))
        name = "mcs_test_component"
        xml = "<?xml version='1.0'?><definition><group type='$var.entryType' name='$var.myentry'/></definition>"
        while name in avc:
            name = name + '_1'
#        print avc
        self.setXML(el, xml)
        self.assertEqual(el.storeComponent(name),None)
        self.__cmps.append(name)
        avc2 = el.availableComponents()
#        print avc2
        self.assertTrue(isinstance(avc2, list))
        for cp in avc:
            self.assertTrue(cp in avc2)
            
        self.assertTrue(name in avc2)


        cpx = el.components([name])
        self.assertEqual(cpx[0], xml)
        
        xml = el.merge([name])

        
        self.assertEqual(
            xml.replace("?>\n<","?><"),
            '<?xml version="1.0" ?><definition><group name="$var.myentry" type="$var.entryType"/></definition>')
        el.variables = '{"myentry":"entry1", "entryType":"NXentry"}'
        xml = el.merge([name])

        self.assertEqual(
            xml.replace("?>\n<","?><"),
            '<?xml version="1.0" ?><definition><group name="$var.myentry" type="$var.entryType"/></definition>')

        self.assertEqual(el.deleteComponent(name),None)
        self.__cmps.pop()
        
        avc3 = el.availableComponents()
        self.assertTrue(isinstance(avc3, list))
        for cp in avc:
            self.assertTrue(cp in avc3)
        self.assertTrue(name not in avc3)


        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 2)
        el.close()






    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_def(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()

        self.assertTrue(isinstance(avc, list))
        name = "mcs_test_component"
        xml = "<group type='NXentry'/>"
        while name in avc:
            name = name + '_1'
#        print avc
        self.setXML(el, xml)
        self.assertEqual(el.storeComponent(name),None)
        self.__cmps.append(name)
        avc2 = el.availableComponents()
#        print avc2
        self.assertTrue(isinstance(avc2, list))
        for cp in avc:
            self.assertTrue(cp in avc2)
            
        self.assertTrue(name in avc2)


        cpx = el.components([name])
        self.assertEqual(cpx[0], xml)
        
        self.myAssertRaise(UndefinedTagError,el.merge,[name])

        self.assertEqual(el.deleteComponent(name),None)
        self.__cmps.pop()
        
        avc3 = el.availableComponents()
        self.assertTrue(isinstance(avc3, list))
        for cp in avc:
            self.assertTrue(cp in avc3)
        self.assertTrue(name not in avc3)


        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 2)
        el.close()



    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_group(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man

        avc = el.availableComponents()

        self.assertTrue(isinstance(avc, list))
        name = ["mcs_test_component"]
        xml = ["<definition/>", "<definition><group type='NXentry'/></definition>"]
        name.append(name[0] +'_2')
        while name[0] in avc:
            name[0] = name[0] + '_1'
        while name[1] in avc:
            name[1] = name[1] + '_2'
#        print avc
        self.setXML(el, xml[0])    
        self.assertEqual(el.storeComponent(name[0]),None)
        self.__cmps.append(name[0])

        self.setXML(el, xml[1])    
        self.assertEqual(el.storeComponent(name[1]),None)
        self.__cmps.append(name[1])

        
        gxml = el.merge(name)
        self.assertEqual(gxml.replace("?>\n<","?><"),
                         '<?xml version="1.0" ?><definition><group type="NXentry"/></definition>')

        self.assertEqual(el.deleteComponent(name[1]),None)
        self.__cmps.pop()

        self.assertEqual(el.deleteComponent(name[0]),None)
        self.__cmps.pop()
        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 4)
        el.close()






    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_group_5(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man

        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = [ "<definition><group type='NXentry'/></definition>"]*5
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        gxml = el.merge(name)
        self.assertEqual(gxml.replace("?>\n<","?><"),'<?xml version="1.0" ?><definition><group type="NXentry"/></definition>')

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 10)
        el.close()





    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_group_group(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ["<definition><group type='NXentry'/></definition>","<definition><group type='NXentry2'/></definition>"]
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        gxml = el.merge(name)
        self.assertTrue((gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition><group type="NXentry2"/><group type="NXentry"/></definition>') |
                        (gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition><group type="NXentry"/><group type="NXentry2"/></definition>') )

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 4)
        el.close()



    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_group_group_error(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man

        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ["<definition><group type='NXentry'/></definition>","<group/>"]
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        self.myAssertRaise(UndefinedTagError,el.merge, name)

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        el.close()



    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_group_group_error_2(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man

        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ["<group/>","<definition><group type='NXentry'/></definition>"]
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        self.myAssertRaise(UndefinedTagError,el.merge, name)

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 4)
        el.close()





    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_group_field_3(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man

        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ["<definition><group type='NXentry'><field type='field'/></group></definition>"]*3
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        gxml = el.merge(name)
        self.assertEqual(gxml.replace("?>\n<","?><"),'<?xml version="1.0" ?><definition><group type="NXentry"><field type="field"/></group></definition>')

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 6)
        el.close()



    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_group_group_field(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man

        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ["<definition><group type='NXentry'><field name='field1'/></group></definition>","<definition><group type='NXentry2'/><field name='field1'/></definition>"]
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        gxml = el.merge(name)
        self.assertTrue((gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition><group type="NXentry2"/><field name="field1"/><group type="NXentry"><field name="field1"/></group></definition>' ) |
                        (gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition><group type="NXentry"><field name="field1"/></group><group type="NXentry2"/><field name="field1"/></definition>' ))

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 4)
        el.close()





    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_group_group_2(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ["<definition><group name='entry'/></definition>","<definition><group type='NXentry2'/></definition>"]
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        gxml = el.merge(name)
        self.assertEqual(gxml.replace("?>\n<","?><"),'<?xml version="1.0" ?><definition><group name="entry" type="NXentry2"/></definition>')

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 4)
        el.close()




    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_group_group_3(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ["<definition><group name='entry'/></definition>","<definition><group name='entry' type='NXentry'/></definition>"]
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        gxml = el.merge(name)
        self.assertEqual(gxml.replace("?>\n<","?><"),'<?xml version="1.0" ?><definition><group name="entry" type="NXentry"/></definition>')

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 4)
        el.close()




    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_group_group_4(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ["<definition><group name='entry2'/></definition>","<definition><group name='entry' type='NXentry'/></definition>"]
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        gxml = el.merge(name)
        self.assertTrue((gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition><group name="entry" type="NXentry"/><group name="entry2"/></definition>') |
                        (gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition><group name="entry2"/><group name="entry" type="NXentry"/></definition>') )

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 4)
        el.close()



    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_group_field_4(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man

        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ["<definition><group type='NXentry'><field type='field'/></group></definition>"]*15
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        gxml = el.merge(name)
        self.assertEqual(gxml.replace("?>\n<","?><"), '<?xml version="1.0" ?><definition><group type="NXentry"><field type="field"/></group></definition>')

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 30)
        el.close()




    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_group_field_5(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man

        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ["<definition><group  name='entry' type='NXentry'><field type='field'/></group></definition>","<definition><group name='entry' type='NXentry'><field type='field'/></group></definition>"]
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        gxml = el.merge(name)
        self.assertEqual(gxml.replace("?>\n<","?><"), '<?xml version="1.0" ?><definition><group name="entry" type="NXentry"><field type="field"/></group></definition>' )

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 4 )
        el.close()




    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_group_field_var(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man

        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ["<definition><group  name='$var.entry' type='NXentry'><field type='field'/></group></definition>","<definition><group name='$var.entry' type='NXentry'><field type='field'>$var.value</field></group></definition>"]
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        el.variables = '{"entry":"entry", "value":"myvalue", "some":"ble"}'
        gxml = el.merge(name)
        self.assertEqual(gxml.replace("?>\n<","?><"), '<?xml version="1.0" ?><definition><group name="$var.entry" type="NXentry"><field type="field">$var.value</field></group></definition>' )

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 4 )
        el.close()




    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_group_field_name_error(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man

        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ["<definition><group  name='entry' type='NXentry'><field type='field'/></group></definition>","<definition><group name='entry' type='NXentry2'><field type='field'/></group></definition>"]
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        self.myAssertRaise(IncompatibleNodeError,el.merge, name)
         
        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 4)
        el.close()



    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_single_name(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man

        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ["<definition><group  name='entry' type='NXentry'><field type='field'/></group></definition>","<definition><group name='entry2' type='NXentry2'><field type='field'/></group></definition>"]
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        gxml = el.merge(name)
        self.assertTrue((gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition><group name="entry2" type="NXentry2"><field type="field"/></group><group name="entry" type="NXentry"><field type="field"/></group></definition>' ) | 
                        (gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition><group name="entry" type="NXentry"><field type="field"/></group><group name="entry2" type="NXentry2"><field type="field"/></group></definition>'))

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 4)
        el.close()



    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_single_name_2_error(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        mr = Merger()
        for sg in mr.singles:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><group  name='entry' type='NXentry'><%s name='field2'/></group></definition>" % sg,"<definition><group name='entry2' type='NXentry2'><%s name='field'/></group></definition>" % sg]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])

        
            self.myAssertRaise(IncompatibleNodeError,el.merge,name)


            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 4)
        el.close()



    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_uniqueText_error(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        mr = Merger()
        for ut in mr.uniqueText:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><group  name='entry' type='NXentry'><%s type='field'>My text </%s></group></definition>" %(ut ,ut),"<definition><group  name='entry' type='NXentry'><%s type='field'>My text 2 </%s></group></definition>" %(ut ,ut)]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])

        
            self.myAssertRaise(IncompatibleNodeError,el.merge,name)

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 4)
        el.close()






    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_children_datasource(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = Merger()
        uts = self.children
        for ut in uts:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><field  name='entry' ><datasource type='TANGO'><%s/></datasource></field></definition>" % ut ]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            gxml = el.merge(name)
            self.assertEqual(gxml.replace("?>\n<","?><"),  '<?xml version="1.0" ?><definition><field name="entry"><datasource type="TANGO"><%s/></datasource></field></definition>' % (ut) )

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision+2)
        el.close()





    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_children_datasource_error(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = Merger()
        uts = []
        for k in el.children:
            for w in el.children[k]:
                if w not in  self.children:
                    uts.append(w)

        uts = set(uts)

        for ut in uts:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><field  name='entry' ><datasource type='TANGO'><%s/></datasource></field></definition>" % ut ]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])

            el.merge(name)

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision+2)
        el.close()




    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_children_attribute(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = Merger()
        uts = el.children['attribute']
        for ut in uts:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><field  name='entry' ><attribute type='TANGO'><%s/></attribute></field></definition>" % ut ]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            gxml = el.merge(name)
            self.assertEqual(gxml.replace("?>\n<","?><"),  '<?xml version="1.0" ?><definition><field name="entry"><attribute type="TANGO"><%s/></attribute></field></definition>' % (ut) )

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision+2)
        el.close()





    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_children_attribute_error(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = Merger()
        uts = []
        for k in el.children:
            for w in el.children[k]:
                if w not in  el.children["attribute"]:
                    uts.append(w)
        uts = set(uts)
        for ut in uts:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><field  name='entry' ><attribute type='TANGO'><%s/></attribute></field></definition>" % ut ]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            self.myAssertRaise(IncompatibleNodeError,el.merge, name)

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision+2)
        el.close()




    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_children_definition(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = Merger()
        uts = el.children['definition']
        for ut in uts:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><%s  name='entry' /></definition>" % ut ]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            
            gxml = el.merge(name)
            self.assertEqual(gxml.replace("?>\n<","?><"),  '<?xml version="1.0" ?><definition><%s name="entry"/></definition>' % (ut) )

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision+2)
        el.close()




    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_children_definition_error(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = Merger()
        uts = []
        for k in el.children:
            for w in el.children[k]:
                if w not in  el.children["definition"]:
                    uts.append(w)

        uts = set(uts)

        for ut in uts:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><%s  name='entry' /></definition>" % ut ]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            self.myAssertRaise(IncompatibleNodeError,el.merge, name)

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision+2)
        el.close()






    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_children_dimensions(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = Merger()
        uts = el.children['dimensions']
        for ut in uts:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><field  name='entry' ><dimensions type='TANGO'><%s/></dimensions></field></definition>" % ut  ]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            
            gxml = el.merge(name)
            self.assertEqual(gxml.replace("?>\n<","?><"),'<?xml version="1.0" ?><definition><field name="entry"><dimensions type="TANGO"><%s/></dimensions></field></definition>' % (ut) )

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision+2 )
        el.close()



    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_children_dimensions_error(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = Merger()
        uts = []
        for k in el.children:
            for w in el.children[k]:
                if w not in  el.children["dimensions"]:
                    uts.append(w)

        uts = set(uts)
        for ut in uts:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><field  name='entry' ><dimensions type='TANGO'><%s/></dimensions></field></definition>" % ut  ]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            self.myAssertRaise(IncompatibleNodeError,el.merge,name)

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision +2)
        el.close()



    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_children_field(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = Merger()
        uts = el.children['field']
        for ut in uts:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><field  name='entry' ><%s/></field></definition>" % ut  ]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            gxml = el.merge(name)
            self.assertEqual(gxml.replace("?>\n<","?><"),'<?xml version="1.0" ?><definition><field name="entry"><%s/></field></definition>' % (ut) )

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision +2 )
        el.close()


    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_children_field_error(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = Merger()
        uts = []
        for k in el.children:
            for w in el.children[k]:
                if w not in  el.children["field"]:
                    uts.append(w)

        uts = set(uts)
        for ut in uts:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><field  name='entry' ><%s/></field></definition>" % ut  ]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            self.myAssertRaise(IncompatibleNodeError,el.merge,name)

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision +2)
        el.close()


    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_children_group(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = Merger()
        uts = el.children['group']
        for ut in uts:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><group  name='entry' ><%s/></group></definition>" % ut  ]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            gxml = el.merge(name)
            self.assertEqual(gxml.replace("?>\n<","?><"),'<?xml version="1.0" ?><definition><group name="entry"><%s/></group></definition>' % (ut) )

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 2)
        el.close()


    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_children_group_error(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = Merger()
        uts = []
        for k in el.children:
            for w in el.children[k]:
                if w not in  el.children["group"]:
                    uts.append(w)

        uts = set(uts)
        for ut in uts:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><group  name='entry' ><%s/></group></definition>" % ut  ]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])

            self.myAssertRaise(IncompatibleNodeError,el.merge,name)


            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 2)
        el.close()





    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_children_link(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = Merger()
        uts = el.children['link']
        for ut in uts:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><link  name='entry' ><%s/></link></definition>" % ut  ]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            gxml = el.merge(name)
            self.assertEqual(gxml.replace("?>\n<","?><"),
                             '<?xml version="1.0" ?><definition><link name="entry"><%s/></link></definition>' % (ut) )

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 2)
        el.close()


    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_children_link_error(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = Merger()
        uts = []
        for k in el.children:
            for w in el.children[k]:
                if w not in  el.children["link"]:
                    uts.append(w)

        uts = set(uts)
        for ut in uts:
        
            el = self.openConfig(self.__args)
            man = el.mandatoryComponents()
            el.unsetMandatoryComponents(man)
            self.__man += man

            avc = el.availableComponents()

            oname = "mcs_test_component"
            self.assertTrue(isinstance(avc, list))
            xml = ["<definition><link  name='entry' ><%s/></link></definition>" % ut  ]
            np = len(xml)
            name = []
            for i in range(np):
                
                name.append(oname +'_%s' % i )
                while name[i] in avc:
                    name[i] = name[i] + '_%s' %i
#        print avc

            for i in range(np):
                self.setXML(el, xml[i])
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            self.myAssertRaise(IncompatibleNodeError,el.merge,name)

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 2)
        el.close()







    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_group_group_mandatory(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ["<definition><group type='NXentry'/></definition>","<definition><group type='NXentry2'/></definition>"]
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        el.setMandatoryComponents([name[0]])
        self.assertEqual(el.mandatoryComponents(),[name[0]])
        

        gxml = el.merge([name[1]])
        self.assertTrue((gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition><group type="NXentry2"/><group type="NXentry"/></definition>') |
                        (gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition><group type="NXentry"/><group type="NXentry2"/></definition>'))

        el.unsetMandatoryComponents([name[0]])
        self.assertEqual(el.mandatoryComponents(),[])

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 6)
        el.close()



    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_group_group_group_mandatory(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()

        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ["<definition><group type='NXentry'/></definition>",
               "<definition><group type='NXentry2'/></definition>",
               "<definition><group type='NXentry3'/></definition>"
               ]
        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        el.setMandatoryComponents([name[0],name[1]])
        self.assertEqual(el.mandatoryComponents().sort(),[name[0],name[1]].sort())

        
        gxml = el.merge([name[2]])

        self.assertTrue( 
            (gxml.replace("?>\n<","?><") ==  '<?xml version="1.0" ?><definition><group type="NXentry2"/><group type="NXentry3"/><group type="NXentry"/></definition>') | 
            (gxml.replace("?>\n<","?><") ==  '<?xml version="1.0" ?><definition><group type="NXentry3"/><group type="NXentry2"/><group type="NXentry"/></definition>') |
            (gxml.replace("?>\n<","?><") ==  '<?xml version="1.0" ?><definition><group type="NXentry3"/><group type="NXentry"/><group type="NXentry2"/></definition>') |
            (gxml.replace("?>\n<","?><") ==  '<?xml version="1.0" ?><definition><group type="NXentry2"/><group type="NXentry"/><group type="NXentry3"/></definition>') |
            (gxml.replace("?>\n<","?><") ==  '<?xml version="1.0" ?><definition><group type="NXentry"/><group type="NXentry2"/><group type="NXentry3"/></definition>') |
            (gxml.replace("?>\n<","?><") ==  '<?xml version="1.0" ?><definition><group type="NXentry"/><group type="NXentry3"/><group type="NXentry2"/></definition>') 
                         )
        

        el.unsetMandatoryComponents([name[1]])


        self.assertEqual(el.mandatoryComponents(),[name[0]])

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        self.assertEqual(el.mandatoryComponents(),[])
        

        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 9)
        el.setMandatoryComponents(man)
        el.close()






    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_componentVariables(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()

        
        vrs =  ["eid", "myvar1","var2", "mvar3"]


        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ['<definition><group type="NXentry" name="entry$var.%s"/><field name="field1">some</field></definition>' 
               % (vrs[0]),
               '<definition><group type="NXentry"/><field name="field2">$var.%s</field></definition>' 
               % (vrs[1]),
               '<definition><group type="NXentry"/><field name="field3">$var.%s</field><field name="field4">$var.%s</field></definition>' 
               % (vrs[2], vrs[3] )
               ]



        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])



        css = [name[0],name[2]]
        cmps = []
        for cs in css:
            mdss = el.componentVariables(cs)
            cmps.extend(mdss)
        self.assertEqual(sorted(cmps),sorted([vrs[0],vrs[2],vrs[3]]))
        
        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision +3)
        el.close()





    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_componentsVariables(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()

        
        vrs =  ["entry_id", "myvar1","var2", "mvar3"]


        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ['<definition><group type="NXentry" name="entry$var.%s"/><field name="field1">some</field></definition>' 
               % (vrs[0]),
               '<definition><group type="NXentry"/><field name="field2">$var.%s</field></definition>' 
               % (vrs[1]),
               '<definition><group type="NXentry"/><field name="field3">$var.%s</field><field name="field4">$var.%s</field></definition>' 
               % (vrs[2], vrs[3] )
               ]



        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])



        css = [name[0],name[2]]
        cmps = []
        mdss = el.componentsVariables(css)
        cmps.extend(mdss)
        self.assertEqual(sorted(cmps),sorted([vrs[0],vrs[2],vrs[3]]))
        
        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision +3)
        el.close()



    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_dependentComponents(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man

        oname = "mcs_test_component"

        avc = el.availableComponents()

        
        vrs =  ["eid", "myvar1","var2", "mvar3"]

        np = 6
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc



        self.assertTrue(isinstance(avc, list))
        xml = ['<definition><group type="NXentry"/><field name="field4"></field><field name="field4"></field>$components.%s$components.%s</definition>' 
               % (name[1], name[2] ),
               '<definition>$components.%s$components.%s<group type="NXentry"/><field name="field5"></field><field name="field4"></field></definition>' 
               % (name[2], name[3] ),
               '<definition><group type="NXentry" name="entry$components.%s"/><field name="field">some</field></definition>' 
               % (name[4]),
               '<definition><group type="NXentry"/><field name="field1">$components.%s</field></definition>' 
               % (name[5]),
               '<definition><group type="NXentry"/><field name="field2"></field><field name="field4"></field></definition>' ,
               '<definition><group type="NXentry"/><field name="field3"></field><field name="field4"></field></definition>' 
               ]



        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])


        arr =[
            [[],[]],
            [[0],[0,1,2,3,4,5]],
            [[1],[1,2,3,4,5]],
            [[2],[2,4]],
            [[3],[3,5]],
            [[4],[4]],
            [[5],[5]],
            [[0,1],[0,1,2,3,4,5]],
            [[0,2],[0,1,2,3,4,5]],
            [[0,3],[0,1,2,3,4,5]],
            [[0,4],[0,1,2,3,4,5]],
            [[0,5],[0,1,2,3,4,5]],
            [[1,2],[1,2,3,4,5]],
            [[1,3],[1,2,3,4,5]],
            [[1,4],[1,2,3,4,5]],
            [[1,5],[1,2,3,4,5]],
            [[2,3],[2,3,4,5]],
            [[2,4],[2,4]],
            [[2,5],[2,4,5]],
            [[3,4],[3,4,5]],
            [[3,5],[3,5]],
            [[4,5],[4,5]],
            [[0,2,1],[0,1,2,3,4,5]],
            [[0,3,1],[0,1,2,3,4,5]],
            [[0,4,1],[0,1,2,3,4,5]],
            [[0,5,1],[0,1,2,3,4,5]],
            [[0,3,2],[0,1,2,3,4,5]],
            [[0,4,2],[0,1,2,3,4,5]],
            [[0,5,2],[0,1,2,3,4,5]],
            [[0,4,3],[0,1,2,3,4,5]],
            [[0,5,3],[0,1,2,3,4,5]],
            [[0,5,4],[0,1,2,3,4,5]],
            [[1,3,2],[1,2,3,4,5]],
            [[1,4,2],[1,2,3,4,5]],
            [[1,5,2],[1,2,3,4,5]],
            [[1,4,3],[1,2,3,4,5]],
            [[1,5,3],[1,2,3,4,5]],
            [[1,5,4],[1,2,3,4,5]],
            [[2,4,3],[2,3,4,5]],
            [[2,5,3],[2,3,4,5]],
            [[2,5,4],[2,4,5]],
            [[3,4,5],[3,4,5]],
            [[0,1,2,3],[0,1,2,3,4,5]],
            [[0,1,2,4],[0,1,2,3,4,5]],
            [[0,1,2,5],[0,1,2,3,4,5]],
            [[0,1,3,4],[0,1,2,3,4,5]],
            [[0,1,3,5],[0,1,2,3,4,5]],
            [[0,1,4,5],[0,1,2,3,4,5]],
            [[1,2,3,4],[1,2,3,4,5]],
            [[1,2,3,5],[1,2,3,4,5]],
            [[1,2,4,5],[1,2,3,4,5]],
            [[1,3,4,5],[1,2,3,4,5]],
            [[2,3,4,5],[2,3,4,5]],
            [[0,1,2,3,4],[0,1,2,3,4,5]],
            [[0,1,2,3,5],[0,1,2,3,4,5]],
            [[0,1,2,4,5],[0,1,2,3,4,5]],
            [[0,1,3,4,5],[0,1,2,3,4,5]],
            [[0,1,3,4,5],[0,1,2,3,4,5]],
            [[0,2,3,4,5],[0,1,2,3,4,5]],
            [[1,2,3,4,5],[1,2,3,4,5]],
            [[0,1,2,3,4,5],[0,1,2,3,4,5]],
            ]    

        for ar in arr:

            css = [name[i]  for  i in ar[0]]
            cmps = []
            mdss = el.dependentComponents(css)
            self.assertEqual(sorted(mdss),sorted([name[i]  for  i in ar[1]]))
        
        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision +6)
        el.close()



    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_dependentComponents_man(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man

        oname = "mcs_test_component"

        avc = el.availableComponents()

        
        vrs =  ["eid", "myvar1","var2", "mvar3"]

        np = 6
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc



        self.assertTrue(isinstance(avc, list))
        xml = ['<definition><group type="NXentry"/><field name="field4"></field><field name="field4"></field>$components.%s$components.%s</definition>' 
               % (name[1], name[2] ),
               '<definition>$components.%s$components.%s<group type="NXentry"/><field name="field5"></field><field name="field4"></field></definition>' 
               % (name[2], name[3] ),
               '<definition><group type="NXentry" name="entry$components.%s"/><field name="field">some</field></definition>' 
               % (name[4]),
               '<definition><group type="NXentry"/><field name="field1">$components.%s</field></definition>' 
               % (name[5]),
               '<definition><group type="NXentry"/><field name="field2"></field><field name="field4"></field></definition>' ,
               '<definition><group type="NXentry"/><field name="field3"></field><field name="field4"></field></definition>' 
               ]



        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])


        arr =[
            [[],[0],[]],
            [[0],[0],[0,1,2,3,4,5]],
            [[1],[0],[1,2,3,4,5]],
            [[2],[2],[2,4]],
            [[3],[0],[3,5]],
            [[4],[1,2],[4]],
            [[5],[3],[5]],
            [[0,1],[0],[0,1,2,3,4,5]],
            [[0,2],[4],[0,1,2,3,4,5]],
            [[0,3],[4],[0,1,2,3,4,5]],
            [[0,4],[0],[0,1,2,3,4,5]],
            [[0,5],[2,5],[0,1,2,3,4,5]],
            [[1,2],[0],[1,2,3,4,5]],
            [[1,3],[2],[1,2,3,4,5]],
            [[1,4],[0],[1,2,3,4,5]],
            [[1,5],[3],[1,2,3,4,5]],
            [[2,3],[4],[2,3,4,5]],
            [[2,4],[0],[2,4]],
            [[2,5],[3],[2,4,5]],
            [[3,4],[0],[3,4,5]],
            [[3,5],[1],[3,5]],
            [[4,5],[0],[4,5]],
            [[0,2,1],[1],[0,1,2,3,4,5]],
            [[0,3,1],[0],[0,1,2,3,4,5]],
            [[0,4,1],[3],[0,1,2,3,4,5]],
            [[0,5,1],[4],[0,1,2,3,4,5]],
            [[0,3,2],[5],[0,1,2,3,4,5]],
            [[0,4,2],[0],[0,1,2,3,4,5]],
            [[0,5,2],[3],[0,1,2,3,4,5]],
            [[0,4,3],[4],[0,1,2,3,4,5]],
            [[0,5,3],[1],[0,1,2,3,4,5]],
            [[0,5,4],[2],[0,1,2,3,4,5]],
            [[1,3,2],[3],[1,2,3,4,5]],
            [[1,4,2],[0],[1,2,3,4,5]],
            [[1,5,2],[4],[1,2,3,4,5]],
            [[1,4,3],[2],[1,2,3,4,5]],
            [[1,5,3],[3],[1,2,3,4,5]],
            [[1,5,4],[1],[1,2,3,4,5]],
            [[2,4,3],[2],[2,3,4,5]],
            [[2,5,3],[3],[2,3,4,5]],
            [[2,5,4],[4],[2,4,5]],
            [[3,4,5],[0,1,2,3,4,5],[3,4,5]],
            [[0,1,2,3],[1],[0,1,2,3,4,5]],
            [[0,1,2,4],[0],[0,1,2,3,4,5]],
            [[0,1,2,5],[1],[0,1,2,3,4,5]],
            [[0,1,3,4],[2],[0,1,2,3,4,5]],
            [[0,1,3,5],[3],[0,1,2,3,4,5]],
            [[0,1,4,5],[4],[0,1,2,3,4,5]],
            [[1,2,3,4],[5],[1,2,3,4,5]],
            [[1,2,3,5],[1],[1,2,3,4,5]],
            [[1,2,4,5],[2],[1,2,3,4,5]],
            [[1,3,4,5],[3],[1,2,3,4,5]],
            [[2,3,4,5],[4],[2,3,4,5]],
            [[0,1,2,3,4],[1],[0,1,2,3,4,5]],
            [[0,1,2,3,5],[2],[0,1,2,3,4,5]],
            [[0,1,2,4,5],[3],[0,1,2,3,4,5]],
            [[0,1,3,4,5],[0],[0,1,2,3,4,5]],
            [[0,1,3,4,5],[2,1,2,3,4],[0,1,2,3,4,5]],
            [[0,2,3,4,5],[3],[0,1,2,3,4,5]],
            [[1,2,3,4,5],[3],[1,2,3,4,5]],
            [[0,1,2,3,4,5],[2],[0,1,2,3,4,5]],
            ]    


        for ar in arr:
            css = [name[i]  for  i in ar[0]]
            cmps = []
            el.setMandatoryComponents([name[i]  for  i in ar[1]])
            mdss = el.dependentComponents(css)
            el.unsetMandatoryComponents([name[i]  for  i in ar[1]])
            self.assertEqual(sorted(mdss),sorted([name[i]  for  i in ar[2]]))
        
        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision +148)
        el.close()





    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_componentDataSources(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()


        xds  = [
            '<datasource name="%s" type="CLIENT"><record name="r1" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r2" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r3" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r4" /></datasource>'
            ]


        odsname = "mcs_test_datasource"
        avds = el.availableDataSources()
        self.assertTrue(isinstance(avds, list))
        dsnp = len(xds)
        dsname = []
        for i in range(dsnp):
            
            dsname.append(odsname +'_%s' % i )
            while dsname[i] in avds:
                dsname[i] = dsname[i] + '_%s' %i

                
        for i in range(dsnp):
            self.setXML(el,xds[i] % dsname[i])
            self.assertEqual(el.storeDataSource(dsname[i]),None)
            self.__ds.append(dsname[i])




        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ['<definition><group type="NXentry"/><field name="field1">%s</field></definition>' 
               % (xds[0] % dsname[0]),
               '<definition><group type="NXentry"/><field name="field2">%s</field></definition>' 
               % (xds[1] % dsname[1]),
               '<definition><group type="NXentry"/><field name="field3">%s</field><field name="field4">%s</field></definition>' 
               % (xds[2] % dsname[2] ,xds[3] % dsname[3] )
               ]



        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])



        css = [name[0],name[2]]
        cmps = []
        for cs in css:
            mdss = el.componentDataSources(cs)
            cmps.extend(mdss)
        self.assertEqual(cmps,[dsname[0],dsname[2],dsname[3]])
        
        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision +7)
        el.close()




    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_componentDataSources_external(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()


        xds  = [
            '<datasource name="%s" type="CLIENT"><record name="r1" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r2" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r3" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r4" /></datasource>'
            ]


        odsname = "mcs_test_datasource"
        avds = el.availableDataSources()
        self.assertTrue(isinstance(avds, list))
        dsnp = len(xds)
        dsname = []
        for i in range(dsnp):
            
            dsname.append(odsname +'_%s' % i )
            while dsname[i] in avds:
                dsname[i] = dsname[i] + '_%s' %i

                
        for i in range(dsnp):
            self.setXML(el, xds[i] % dsname[i])
            self.assertEqual(el.storeDataSource(dsname[i]),None)
            self.__ds.append(dsname[i])




        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ['<definition><group type="NXentry"/><field name="field1">%s</field></definition>' 
               % ("$datasources.%s" % dsname[0]),
               '<definition><group type="NXentry"/><field name="field2">%s</field></definition>' 
               % ("$datasources.%s" % dsname[1]),
               '<definition><group type="NXentry"/><field name="field3">%s</field><field name="field4">%s</field></definition>' 
               % ("$datasources.%s" % dsname[2] ,"$datasources.%s" % dsname[3] )
               ]



        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])



        css = [name[0],name[2]]
        cmps = []
        for cs in css:
            mdss = el.componentDataSources(cs)
            cmps.extend(mdss)
        self.assertEqual(cmps,[dsname[0],dsname[2],dsname[3]])
        
        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision+7)
        el.close()







    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_componentDataSources_external_2(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()


        xds  = [
            '<datasource name="%s" type="CLIENT"><record name="r1" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r2" /></datasource>'
            ]


        odsname = "mcs_test_datasource"
        avds = el.availableDataSources()
        self.assertTrue(isinstance(avds, list))
        dsnp = len(xds)
        dsname = []
        dsname.append(odsname +'_1')
        dsname.append(odsname +'_11')
        rename = odsname
        while dsname[0] in avds or dsname[1] in avds:
            rename = rename + "_1"
            dsname[0] = rename + '_1'
            dsname[1] = rename + '_11'
            print "AVDS", avds 
            print "WW ", rename, dsname[0], dsname[1]
                
        for i in range(dsnp):
            self.setXML(el, xds[i] % dsname[i])
            self.assertEqual(el.storeDataSource(dsname[i]),None)
            self.__ds.append(dsname[i])




        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ['<definition><group type="NXentry"/><field name="field1">%s</field></definition>' 
               % ("$datasources.%s" % dsname[0]),
               '<definition><group type="NXentry"/><field name="field2">%s</field></definition>' 
               % ("$datasources.%s" % dsname[1]),
               '<definition><group type="NXentry"/><field name="field3">%s</field><field name="field4">%s</field></definition>' 
               % ("$datasources.%s" % dsname[0] ,"$datasources.%s" % dsname[1] )
               ]



        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])



        css = [name[0],name[2]]
        cmps = []
        for cs in css:
            mdss = el.componentDataSources(cs)
            cmps.extend(mdss)
        self.assertEqual(sorted(cmps),sorted([dsname[0],dsname[1],dsname[0]]))
        
        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision+5)
        el.close()



    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_componentDataSources_external_2_double(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()


        xds  = [
            '<datasource name="%s" type="CLIENT"><record name="r1" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r2" /></datasource>'
            ]


        odsname = "mcs_test_datasource"
        avds = el.availableDataSources()
        self.assertTrue(isinstance(avds, list))
        dsnp = len(xds)
        dsname = []
        dsname.append(odsname +'_1')
        dsname.append(odsname +'_11')
        rename = odsname
        while dsname[0] in avds or dsname[1] in avds:
            rename = rename + "_1"
            dsname[0] = rename + '_1'
            dsname[1] = rename + '_11'

                
        for i in range(dsnp):
            self.setXML(el, xds[i] % dsname[i])
            self.assertEqual(el.storeDataSource(dsname[i]),None)
            self.__ds.append(dsname[i])




        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ['<definition><group type="NXentry"/><field name="field1">%s</field></definition>' 
               % ("$datasources.%s" % dsname[0]),
               '<definition><group type="NXentry"/><field name="field2">%s</field></definition>' 
               % ("$datasources.%s" % dsname[1]),
               '<definition><group type="NXentry"/><field name="field3"><datasource>%s%s</datasource></field></definition>' 
               % ("$datasources.%s" % dsname[0] ,"$datasources.%s" % dsname[1] )
               ]



        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])



        css = [name[0],name[2]]
        cmps = []
        for cs in css:
            mdss = el.componentDataSources(cs)
            cmps.extend(mdss)
        self.assertEqual(cmps,[dsname[0], '__unnamed__0'])
        
        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision+5)
        el.close()



    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_componentDataSources_mixed(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()


        xds  = [
            '<datasource name="%s" type="CLIENT"><record name="r1" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r2" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r3" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r4" /></datasource>'
            ]


        odsname = "mcs_test_datasource"
        avds = el.availableDataSources()
        self.assertTrue(isinstance(avds, list))
        dsnp = len(xds)
        dsname = []
        for i in range(dsnp):
            
            dsname.append(odsname +'_%s' % i )
            while dsname[i] in avds:
                dsname[i] = dsname[i] + '_%s' %i

                
        for i in range(dsnp):
            self.setXML(el, xds[i] % dsname[i])
            self.assertEqual(el.storeDataSource(dsname[i]),None)
            self.__ds.append(dsname[i])
            


        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ['<definition><group type="NXentry"/><field name="field1">%s</field></definition>' 
               % (xds[0] % dsname[0]),
               '<definition><group type="NXentry"/><field name="field2">%s</field></definition>' 
               % ("$datasources.%s" % dsname[1]),
               '<definition><group type="NXentry"/><field name="field3">%s</field><field name="field4">%s</field></definition>' 
               % (xds[2] % dsname[2] ,"$datasources.%s" % dsname[3] )
               ]



        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])



        css = [name[0],name[2]]
        cmps = []
        for cs in css:
            mdss = el.componentDataSources(cs)
            print mdss
            cmps.extend(mdss)
        self.assertEqual(cmps,[dsname[0],dsname[2],dsname[3]])
        
        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision +7)
        el.close()













    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_componentsDataSources(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()


        xds  = [
            '<datasource name="%s" type="CLIENT"><record name="r1" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r2" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r3" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r4" /></datasource>'
            ]


        odsname = "mcs_test_datasource"
        avds = el.availableDataSources()
        self.assertTrue(isinstance(avds, list))
        dsnp = len(xds)
        dsname = []
        for i in range(dsnp):
            
            dsname.append(odsname +'_%s' % i )
            while dsname[i] in avds:
                dsname[i] = dsname[i] + '_%s' %i

                
        for i in range(dsnp):
            self.setXML(el,xds[i] % dsname[i])
            self.assertEqual(el.storeDataSource(dsname[i]),None)
            self.__ds.append(dsname[i])




        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ['<definition><group type="NXentry"/><field name="field1">%s</field></definition>' 
               % (xds[0] % dsname[0]),
               '<definition><group type="NXentry"/><field name="field2">%s</field></definition>' 
               % (xds[1] % dsname[1]),
               '<definition><group type="NXentry"/><field name="field3">%s</field><field name="field4">%s</field></definition>' 
               % (xds[2] % dsname[2] ,xds[3] % dsname[3] )
               ]



        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])



        css = [name[0],name[2]]
        cmps = []
        mdss = el.componentsDataSources(css)
        cmps.extend(mdss)
        self.assertEqual(sorted(cmps),sorted([dsname[0],dsname[2],dsname[3]]))
        
        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision +7)
        el.close()




    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_componentsDataSources_man(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()


        xds  = [
            '<datasource name="%s" type="CLIENT"><record name="r1" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r2" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r3" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r4" /></datasource>'
            ]


        odsname = "mcs_test_datasource"
        avds = el.availableDataSources()
        self.assertTrue(isinstance(avds, list))
        dsnp = len(xds)
        dsname = []
        for i in range(dsnp):
            
            dsname.append(odsname +'_%s' % i )
            while dsname[i] in avds:
                dsname[i] = dsname[i] + '_%s' %i

                
        for i in range(dsnp):
            self.setXML(el,xds[i] % dsname[i])
            self.assertEqual(el.storeDataSource(dsname[i]),None)
            self.__ds.append(dsname[i])




        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ['<definition><group type="NXentry"/><field name="field1">%s</field></definition>' 
               % (xds[0] % dsname[0]),
               '<definition><group type="NXentry"/><field name="field2">%s</field></definition>' 
               % (xds[1] % dsname[1]),
               '<definition><group type="NXentry"/><field name="field3">%s</field><field name="field4">%s</field></definition>' 
               % (xds[2] % dsname[2] ,xds[3] % dsname[3] )
               ]



        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        el.setMandatoryComponents([name[0]])


        css = [name[2]]
        cmps = []
        mdss = el.componentsDataSources(css)
        cmps.extend(mdss)
        self.assertEqual(sorted(cmps),sorted([dsname[0],dsname[2],dsname[3]]))
        
        
        el.unsetMandatoryComponents([name[0]])

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision +9)
        el.close()




    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_componentsDataSources_external(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()


        xds  = [
            '<datasource name="%s" type="CLIENT"><record name="r1" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r2" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r3" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r4" /></datasource>'
            ]


        odsname = "mcs_test_datasource"
        avds = el.availableDataSources()
        self.assertTrue(isinstance(avds, list))
        dsnp = len(xds)
        dsname = []
        for i in range(dsnp):
            
            dsname.append(odsname +'_%s' % i )
            while dsname[i] in avds:
                dsname[i] = dsname[i] + '_%s' %i

                
        for i in range(dsnp):
            self.setXML(el, xds[i] % dsname[i])
            self.assertEqual(el.storeDataSource(dsname[i]),None)
            self.__ds.append(dsname[i])




        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ['<definition><group type="NXentry"/><field name="field1">%s</field></definition>' 
               % ("$datasources.%s" % dsname[0]),
               '<definition><group type="NXentry"/><field name="field2">%s</field></definition>' 
               % ("$datasources.%s" % dsname[1]),
               '<definition><group type="NXentry"/><field name="field3">%s</field><field name="field4">%s</field></definition>' 
               % ("$datasources.%s" % dsname[2] ,"$datasources.%s" % dsname[3] )
               ]



        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])



        css = [name[0],name[2]]
        cmps = []
        mdss = el.componentsDataSources(css)
        cmps.extend(mdss)
        self.assertEqual(sorted(cmps), sorted([dsname[0],dsname[2],dsname[3]]))
        
        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision+7)
        el.close()







    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_componentsDataSources_external_2(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()


        xds  = [
            '<datasource name="%s" type="CLIENT"><record name="r1" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r2" /></datasource>'
            ]


        odsname = "mcs_test_datasource"
        avds = el.availableDataSources()
        self.assertTrue(isinstance(avds, list))
        dsnp = len(xds)
        dsname = []
        dsname.append(odsname +'_1')
        dsname.append(odsname +'_11')
        rename = odsname
        while dsname[0] in avds or dsname[1] in avds:
            rename = rename + "_1"
            dsname[0] = rename + '_1'
            dsname[1] = rename + '_11'

                
        for i in range(dsnp):
            self.setXML(el, xds[i] % dsname[i])
            self.assertEqual(el.storeDataSource(dsname[i]),None)
            self.__ds.append(dsname[i])




        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ['<definition><group type="NXentry"/><field name="field1">%s</field></definition>' 
               % ("$datasources.%s" % dsname[0]),
               '<definition><group type="NXentry"/><field name="field2">%s</field></definition>' 
               % ("$datasources.%s" % dsname[1]),
               '<definition><group type="NXentry"/><field name="field3">%s</field><field name="field4">%s</field></definition>' 
               % ("$datasources.%s" % dsname[0] ,"$datasources.%s" % dsname[1] )
               ]



        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])



        css = [name[0],name[2]]
        cmps = []
        mdss = el.componentsDataSources(css)
        cmps.extend(mdss)
        self.assertEqual(sorted(cmps), sorted([dsname[0],dsname[1]]))
        
        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision+5)
        el.close()



    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_componentsDataSources_external_2_double(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()


        xds  = [
            '<datasource name="%s" type="CLIENT"><record name="r1" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r2" /></datasource>'
            ]


        odsname = "mcs_test_datasource"
        avds = el.availableDataSources()
        self.assertTrue(isinstance(avds, list))
        dsnp = len(xds)
        dsname = []
        dsname.append(odsname +'_1')
        dsname.append(odsname +'_11')
        rename = odsname
        while dsname[0] in avds or dsname[1] in avds:
            rename = rename + "_1"
            dsname[0] = rename + '_1'
            dsname[1] = rename + '_11'

                
        for i in range(dsnp):
            self.setXML(el, xds[i] % dsname[i])
            self.assertEqual(el.storeDataSource(dsname[i]),None)
            self.__ds.append(dsname[i])




        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ['<definition><group type="NXentry"/><field name="field1">%s</field></definition>' 
               % ("$datasources.%s" % dsname[0]),
               '<definition><group type="NXentry"/><field name="field2">%s</field></definition>' 
               % ("$datasources.%s" % dsname[1]),
               '<definition><group type="NXentry"/><field name="field3"><datasource>%s%s</datasource></field></definition>' 
               % ("$datasources.%s" % dsname[0] ,"$datasources.%s" % dsname[1] )
               ]



        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])



        css = [name[0],name[2]]
        cmps = []
        mdss = el.componentsDataSources(css)
        cmps.extend(mdss)
        self.assertEqual(sorted(cmps),sorted([dsname[0], '__unnamed__0']))
        
        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision+5)
        el.close()



    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_componentsDataSources_mixed(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()


        xds  = [
            '<datasource name="%s" type="CLIENT"><record name="r1" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r2" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r3" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r4" /></datasource>'
            ]


        odsname = "mcs_test_datasource"
        avds = el.availableDataSources()
        self.assertTrue(isinstance(avds, list))
        dsnp = len(xds)
        dsname = []
        for i in range(dsnp):
            
            dsname.append(odsname +'_%s' % i )
            while dsname[i] in avds:
                dsname[i] = dsname[i] + '_%s' %i

                
        for i in range(dsnp):
            self.setXML(el, xds[i] % dsname[i])
            self.assertEqual(el.storeDataSource(dsname[i]),None)
            self.__ds.append(dsname[i])
            


        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ['<definition><group type="NXentry"/><field name="field1">%s</field></definition>' 
               % (xds[0] % dsname[0]),
               '<definition><group type="NXentry"/><field name="field2">%s</field></definition>' 
               % ("$datasources.%s" % dsname[1]),
               '<definition><group type="NXentry"/><field name="field3">%s</field><field name="field4">%s</field></definition>' 
               % (xds[2] % dsname[2] ,"$datasources.%s" % dsname[3] )
               ]



        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])



        css = [name[0],name[2]]
        cmps = []
        mdss = el.componentsDataSources(css)
        print mdss
        cmps.extend(mdss)
        self.assertEqual(sorted(cmps),sorted([dsname[0],dsname[2],dsname[3]]))
        
        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision +7)
        el.close()








    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConfiguration_mixed(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()


        xds  = [
            '<datasource name="%s" type="CLIENT"><record name="r1" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r2" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r3" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r4" /></datasource>'
            ]


        odsname = "mcs_test_datasource"
        avds = el.availableDataSources()
        self.assertTrue(isinstance(avds, list))
        dsnp = len(xds)
        dsname = []
        for i in range(dsnp):
            
            dsname.append(odsname +'_%s' % i )
            while dsname[i] in avds:
                dsname[i] = dsname[i] + '_%s' %i

                
        for i in range(dsnp):
            self.setXML(el, xds[i] % dsname[i])
            self.assertEqual(el.storeDataSource(dsname[i]),None)
            print "DS store", dsname[i]
            self.__ds.append(dsname[i])

        print "AVAIL", el.availableDataSources()    




        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ['<definition><group type="NXentry"/><field name="field1">%s</field></definition>' % ("$datasources.%s" % dsname[0]),
               '<definition><group type="NXentry"/><field name="field2">%s</field></definition>' % ("$datasources.%s" % dsname[1]),
               '<definition><group type="NXentry"/><field name="field3">%s</field><field name="field4">%s</field></definition>' 
               % (xds[2] % dsname[2] ,"$datasources.%s" % dsname[3] )
               ]



        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])



        css = [name[0],name[2]]
        print "AVAIL2", el.availableDataSources()    

        self.assertEqual(el.createConfiguration(css), None)
        gxml = self.getXML(el)
        self.assertTrue((gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition> <group type="NXentry"/> <field name="field3">  <datasource name="%s" type="CLIENT">   <record name="r3"/>  </datasource> </field> <field name="field4">  \n  <datasource name="%s" type="CLIENT">   <record name="r4"/>  </datasource> </field> <field name="field1">  \n  <datasource name="%s" type="CLIENT">   <record name="r1"/>  </datasource> </field></definition>' % ( dsname[2], dsname[3], dsname[0] ) ) |
                        (gxml.replace("?>\n<","?><") ==   '<?xml version="1.0" ?><definition> <group type="NXentry"/> <field name="field1">  \n  <datasource name="%s" type="CLIENT">   <record name="r1"/>  </datasource> </field> <field name="field3">  <datasource name="%s" type="CLIENT">   <record name="r3"/>  </datasource> </field> <field name="field4">  \n  <datasource name="%s" type="CLIENT">   <record name="r4"/>  </datasource> </field></definition>' % ( dsname[0], dsname[2], dsname[3] ) ))

        

      
        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 7)
        el.close()






    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConfiguration_mixed_var(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()


        xds  = [
            '<datasource name="%s" type="CLIENT"><record name="$var.name1" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="$var.name2" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="$var.name3" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="$var.name4" /></datasource>'
            ]


        odsname = "mcs_test_datasource"
        avds = el.availableDataSources()
        self.assertTrue(isinstance(avds, list))
        dsnp = len(xds)
        dsname = []
        for i in range(dsnp):
            
            dsname.append(odsname +'_%s' % i )
            while dsname[i] in avds:
                dsname[i] = dsname[i] + '_%s' %i

                
        for i in range(dsnp):
            self.setXML(el, xds[i] % dsname[i])
            self.assertEqual(el.storeDataSource(dsname[i]),None)
            print "DS store", dsname[i]
            self.__ds.append(dsname[i])

        print "AVAIL", el.availableDataSources()    




        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ['<definition><group type="NXentry"/><field name="field1">%s</field></definition>' % ("$datasources.%s" % dsname[0]),
               '<definition><group type="NXentry"/><field name="field2">%s</field></definition>' % ("$datasources.%s" % dsname[1]),
               '<definition><group type="NXentry"/><field name="field3">%s</field><field name="field4">%s</field></definition>' 
               % (xds[2] % dsname[2] ,"$datasources.%s" % dsname[3] )
               ]



        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])



        css = [name[0],name[2]]
        print "AVAIL2", el.availableDataSources()    

        el.variables = '{"name1":"r1","name2":"r2","name3":"r3","name4":"r4"}'
        self.assertEqual(el.createConfiguration(css), None)
        gxml = self.getXML(el)
        self.assertTrue((gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition> <group type="NXentry"/> <field name="field3">  <datasource name="%s" type="CLIENT">   <record name="r3"/>  </datasource> </field> <field name="field4">  \n  <datasource name="%s" type="CLIENT">   <record name="r4"/>  </datasource> </field> <field name="field1">  \n  <datasource name="%s" type="CLIENT">   <record name="r1"/>  </datasource> </field></definition>' % ( dsname[2], dsname[3], dsname[0] ) ) |
                        (gxml.replace("?>\n<","?><") ==  '<?xml version="1.0" ?><definition> <group type="NXentry"/> <field name="field1">  \n  <datasource name="%s" type="CLIENT">   <record name="r1"/>  </datasource> </field> <field name="field3">  <datasource name="%s" type="CLIENT">   <record name="r3"/>  </datasource> </field> <field name="field4">  \n  <datasource name="%s" type="CLIENT">   <record name="r4"/>  </datasource> </field></definition>'% ( dsname[0], dsname[2], dsname[3] ) )  )

        

      
        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 7)
        el.close()







    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConfiguration_mixed_var_1(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()


        xds  = [
            '<datasource name="%s" type="CLIENT"><record name="$var.name1" /></datasource>',
            ]


        odsname = "mcs_test_datasource"
        avds = el.availableDataSources()
        self.assertTrue(isinstance(avds, list))
        dsnp = len(xds)
        dsname = []
        for i in range(dsnp):
            
            dsname.append(odsname +'_%s' % i )
            while dsname[i] in avds:
                dsname[i] = dsname[i] + '_%s' %i

                
        for i in range(dsnp):
            self.setXML(el, xds[i] % dsname[i])
            self.assertEqual(el.storeDataSource(dsname[i]),None)
            print "DS store", dsname[i]
            self.__ds.append(dsname[i])

        print "AVAIL", el.availableDataSources()    




        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = [
            '<definition><group type="NXentry"/><field name="field">%s</field></definition>' % (xds[0] % dsname[0]),
            '<definition><group type="NXentry"/><field name="field">%s</field></definition>' % ("$datasources.$var.source"),
            '<definition><group type="NXentry"/><field name="field">%s</field></definition>' % ("$datasources.%s" % dsname[0])
               ]



        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])



        css = [name[i] for i in range(len(xml))]
        print "AVAIL2", el.availableDataSources()    

        el.variables = '{"name1":"r1","source":"%s"}' % dsname[0]
        self.assertEqual(el.createConfiguration(css), None)
        gxml = self.getXML(el)
        self.assertEqual(gxml.replace("?>\n<","?><"), '<?xml version="1.0" ?><definition> <group type="NXentry"/> <field name="field">  \n  <datasource name="%s" type="CLIENT">   <record name="r1"/>  </datasource> </field></definition>'   % ( dsname[0] )  )

        

      
        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 4)
        el.close()







    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConfiguration_mixed_var_2(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()


        xds  = [
            '<datasource name="%s" type="CLIENT"><record name="$var.name1" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="$var.name2" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="$var.name3" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="$var.name5" /></datasource>'
            ]


        odsname = "mcs_test_datasource"
        avds = el.availableDataSources()
        self.assertTrue(isinstance(avds, list))
        dsnp = len(xds)
        dsname = []
        for i in range(dsnp):
            
            dsname.append(odsname +'_%s' % i )
            while dsname[i] in avds:
                dsname[i] = dsname[i] + '_%s' %i

                
        for i in range(dsnp):
            self.setXML(el, xds[i] % dsname[i])
            self.assertEqual(el.storeDataSource(dsname[i]),None)
            print "DS store", dsname[i]
            self.__ds.append(dsname[i])

        print "AVAIL", el.availableDataSources()    




        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ['<definition><group type="NXentry"/><field name="field1">%s</field></definition>' % ("$datasources.%s" % dsname[0]),
               '<definition><group type="NXentry"/><field name="field2">%s</field></definition>' % ("$datasources.%s" % dsname[1]),
               '<definition><group type="NXentry"/><field name="field3">%s</field><field name="field4">%s</field></definition>' 
               % (xds[2] % dsname[2] ,"$datasources.%s" % dsname[3] )
               ]



        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])



        css = [name[0],name[2]]
        print "AVAIL2", el.availableDataSources()    

        el.variables = '{"name1":"r1","name2":"r2","name3":"r3","name4":"r4"}'
        self.assertEqual(el.createConfiguration(css), None)
        gxml = self.getXML(el)
        self.assertTrue((gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition> <group type="NXentry"/> <field name="field3">  <datasource name="%s" type="CLIENT">   <record name="r3"/>  </datasource> </field> <field name="field4">  \n  <datasource name="%s" type="CLIENT">   <record name=""/>  </datasource> </field> <field name="field1">  \n  <datasource name="%s" type="CLIENT">   <record name="r1"/>  </datasource> </field></definition>' % ( dsname[2], dsname[3], dsname[0] ) ) |
                        (gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition> <group type="NXentry"/> <field name="field1">  \n  <datasource name="%s" type="CLIENT">   <record name="r1"/>  </datasource> </field> <field name="field3">  <datasource name="%s" type="CLIENT">   <record name="r3"/>  </datasource> </field> <field name="field4">  \n  <datasource name="%s" type="CLIENT">   <record name=""/>  </datasource> </field></definition>' % ( dsname[0], dsname[2], dsname[3] ) ))

        

      
        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 7)
        el.close()








    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConfiguration_mixed_2(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()


        xds  = [
            '<datasource name="%s" type="CLIENT"><record name="r1" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r2" /></datasource>'
            ]



        odsname = "mcs_test_datasource"
        avds = el.availableDataSources()
        self.assertTrue(isinstance(avds, list))
        dsnp = len(xds)
        dsname = []
        dsname.append(odsname +'_1')
        dsname.append(odsname +'_11')
        rename = odsname
        while dsname[0] in avds or dsname[1] in avds:
            rename = rename + "_1"
            dsname[0] = rename + '_1'
            dsname[1] = rename + '_11'
                
        for i in range(dsnp):
            self.setXML(el, xds[i] % dsname[i])
            self.assertEqual(el.storeDataSource(dsname[i]),None)
            print "DS store", dsname[i]
            self.__ds.append(dsname[i])

        print "AVAIL", el.availableDataSources()    




        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ['<definition><group type="NXentry"/><field name="field1">%s</field></definition>' % ("$datasources.%s" % dsname[0]),
               '<definition><group type="NXentry"/><field name="field2">%s</field></definition>' % ("$datasources.%s" % dsname[1]),
               '<definition><group type="NXentry"/><field name="field3">%s</field><field name="field4">%s</field></definition>' 
               % (xds[0] % dsname[0] ,"$datasources.%s" % dsname[1] ),
               '<definition><group type="NXentry"/><field name="field3">%s</field><field name="field4">%s</field></definition>' 
               % ("$datasources.%s" % dsname[0] ,"$datasources.%s" % dsname[1] )
               ]



        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])



        css = [name[0],name[2]]
        print "AVAIL2", el.availableDataSources()    

        self.assertEqual(el.createConfiguration(css), None)
        gxml = self.getXML(el)
        self.assertTrue((gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition> <group type="NXentry"/> <field name="field3">  <datasource name="%s" type="CLIENT">   <record name="r1"/>  </datasource> </field> <field name="field4">  \n  <datasource name="%s" type="CLIENT">   <record name="r2"/>  </datasource> </field> <field name="field1">  \n  <datasource name="%s" type="CLIENT">   <record name="r1"/>  </datasource> </field></definition>' % (dsname[0],dsname[1],dsname[0])) |
                        (gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition> <group type="NXentry"/> <field name="field1">  \n  <datasource name="%s" type="CLIENT">   <record name="r1"/>  </datasource> </field> <field name="field3">  <datasource name="%s" type="CLIENT">   <record name="r1"/>  </datasource> </field> <field name="field4">  \n  <datasource name="%s" type="CLIENT">   <record name="r2"/>  </datasource> </field></definition>' % (dsname[0],dsname[0],dsname[1])))

        
        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 6)
        el.close()





    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConfiguration_mixed_2_double(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()


        xds  = [
            '<datasource name="%s" type="CLIENT"><record name="r1" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r2" /></datasource>'
            ]



        odsname = "mcs_test_datasource"
        avds = el.availableDataSources()
        self.assertTrue(isinstance(avds, list))
        dsnp = len(xds)
        dsname = []
        dsname.append(odsname +'_1')
        dsname.append(odsname +'_11')
        rename = odsname
        while dsname[0] in avds or dsname[1] in avds:
            rename = rename + "_1"
            dsname[0] = rename + '_1'
            dsname[1] = rename + '_11'
                
        for i in range(dsnp):
            self.setXML(el, xds[i] % dsname[i])
            self.assertEqual(el.storeDataSource(dsname[i]),None)
            print "DS store", dsname[i]
            self.__ds.append(dsname[i])

        print "AVAIL", el.availableDataSources()    




        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ['<definition><group type="NXentry"/><field name="field1">%s</field></definition>' % ("$datasources.%s" % dsname[0]),
               '<definition><group type="NXentry"/><field name="field2">%s</field></definition>' % ("$datasources.%s" % dsname[1]),
               '<definition><group type="NXentry"/><field name="field3">%s</field><field name="field4">%s</field></definition>' 
               % (xds[0] % dsname[0] ,"$datasources.%s" % dsname[1] ),
               '<definition><group type="NXentry"/><field name="field3"><datasource>%s%s</datasource></field></definition>' 
               % ("$datasources.%s" % dsname[0] ,"$datasources.%s" % dsname[1] )
               ]



        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])



        css = [name[0], name[3]]
        print "AVAIL2", el.availableDataSources()    

        self.assertEqual(el.createConfiguration(css), None)
        gxml = self.getXML(el)
        print "GXML2:\n", gxml
        self.assertTrue((gxml.replace("?>\n<","?><") ==  '<?xml version="1.0" ?><definition> <group type="NXentry"/> <field name="field3">  <datasource>   \n   <datasource name="%s" type="CLIENT">    <record name="r1"/>   </datasource>   \n   <datasource name="%s" type="CLIENT">    <record name="r2"/>   </datasource>  </datasource> </field> <field name="field1">  \n  <datasource name="%s" type="CLIENT">   <record name="r1"/>  </datasource> </field></definition>' % (dsname[0], dsname[1], dsname[0] )) |
                        (gxml.replace("?>\n<","?><") ==  '<?xml version="1.0" ?><definition> <group type="NXentry"/> <field name="field1">  \n  <datasource name="%s" type="CLIENT">   <record name="r1"/>  </datasource> </field> <field name="field3">  <datasource>   \n   <datasource name="%s" type="CLIENT">    <record name="r1"/>   </datasource>   \n   <datasource name="%s" type="CLIENT">    <record name="r2"/>   </datasource>  </datasource> </field></definition>'  % (dsname[0], dsname[0], dsname[1] ))
)

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 6)
        el.close()





    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConfiguration_mixed_3_double(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()


        xds  = [
            '<datasource name="%s" type="CLIENT"><record name="r1" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r2" /></datasource>',
            """<datasource name="%s" type="CLIENT">$datasources.%s$datasources.%s<result>
import ndts
ds.result = ndts.version</result></datasource>"""
            ]



        odsname = "mcs_test_datasource"
        avds = el.availableDataSources()
        self.assertTrue(isinstance(avds, list))
        dsnp = len(xds)
        dsname = []
        dsname.append(odsname +'_1')
        dsname.append(odsname +'_11')
        dsname.append(odsname +'_111')
        rename = odsname
        while dsname[0] in avds or dsname[1] in avds or dsname[2] in avds:
            rename = rename + "_1"
            dsname[0] = rename + '_1'
            dsname[1] = rename + '_11'
            dsname[2] = rename + '_111'
                
        for i in range(dsnp):
            if i < 2:
                self.setXML(el, xds[i] % dsname[i])
            else:
                self.setXML(el, xds[i] % (dsname[2], dsname[0], dsname[1]))
            self.assertEqual(el.storeDataSource(dsname[i]),None)
            print "DS store", dsname[i]
            self.__ds.append(dsname[i])

        print "AVAIL", el.availableDataSources()    




        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ['<definition><group type="NXentry"/><field name="field1">%s</field></definition>' % ("$datasources.%s" % dsname[0]),
               '<definition><group type="NXentry"/><field name="field2">%s</field></definition>' % ("$datasources.%s" % dsname[1]),
               '<definition><group type="NXentry"/><field name="field3">%s</field><field name="field4">%s</field></definition>' 
               % (xds[0] % dsname[0] ,"$datasources.%s" % dsname[1] ),
               '<definition><group type="NXentry"/><field name="field3">%s</field></definition>' 
               % ("$datasources.%s" % dsname[2] )
               ]



        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])



        css = [name[0], name[3]]
        print "AVAIL2", el.availableDataSources()    

        self.assertEqual(el.createConfiguration(css), None)
        gxml = self.getXML(el)
        print "GXML3:\n", gxml
        
        mxml = gxml.replace(">    ",">").replace(">   ",">").replace(">  ",">").replace("> ",">")\
            .replace("    <","<").replace("   <","<").replace("  <","<").replace(" <","<")\
            .replace("?>\n<","?><")
        self.assertTrue((mxml == '<?xml version="1.0" ?><definition><group type="NXentry"/><field name="field3">\n<datasource name="%s" type="CLIENT">\n<datasource name="%s" type="CLIENT"><record name="r1"/></datasource>\n<datasource name="%s" type="CLIENT"><record name="r2"/></datasource><result>\nimport ndts\nds.result = ndts.version</result></datasource></field><field name="field1">\n<datasource name="%s" type="CLIENT"><record name="r1"/></datasource></field></definition>' % (dsname[2], dsname[0], dsname[1], dsname[0])) |  
                        (mxml == '<?xml version="1.0" ?><definition><group type="NXentry"/><field name="field1">\n<datasource name="%s" type="CLIENT"><record name="r1"/></datasource></field><field name="field3">\n<datasource name="%s" type="CLIENT">\n<datasource name="%s" type="CLIENT"><record name="r1"/></datasource>\n<datasource name="%s" type="CLIENT"><record name="r2"/></datasource><result>\nimport ndts\nds.result = ndts.version</result></datasource></field></definition>' % (dsname[0], dsname[2], dsname[0], dsname[1])))
        
        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 7)
        el.close()




    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConfiguration_mixed_definition(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()


        xds  = [
            '<datasource name="%s" type="CLIENT"><record name="r1" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r2" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r3" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r4" /></datasource>'
            ]
 

        odsname = "mcs_test_datasource"
        avds = el.availableDataSources()
        self.assertTrue(isinstance(avds, list))
        dsnp = len(xds)
        dsname = []
        for i in range(dsnp):
            
            dsname.append(odsname +'_%s' % i )
            while dsname[i] in avds:
                dsname[i] = dsname[i] + '_%s' %i

                
        for i in range(dsnp):
            self.setXML(el, "<?xml version=\'1.0\'?><definition>%s</definition>" % (xds[i] % dsname[i]))
            self.assertEqual(el.storeDataSource(dsname[i]),None)
            self.__ds.append(dsname[i])




        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ['<definition><group type="NXentry"/><field name="field1">%s</field></definition>' % ("$datasources.%s" % dsname[0]),
               '<definition><group type="NXentry"/><field name="field2">%s</field></definition>' % ("$datasources.%s" % dsname[1]),
               '<definition><group type="NXentry"/><field name="field3">%s</field><field name="field4">%s</field></definition>' 
               % (xds[2] % dsname[2] ,"$datasources.%s" % dsname[3] )
               ]



        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i] )
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])



        css = [name[0],name[2]]
        print el.components([name[0],name[2]])
        print "CSS",css
        print "MAND", el.mandatoryComponents()
        self.assertEqual(el.createConfiguration(css), None)
        gxml = self.getXML(el)
        self.assertTrue((gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition> <group type="NXentry"/> <field name="field3">  <datasource name="%s" type="CLIENT">   <record name="r3"/>  </datasource> </field> <field name="field4">  \n  <datasource name="%s" type="CLIENT">   <record name="r4"/>  </datasource> </field> <field name="field1">  \n  <datasource name="%s" type="CLIENT">   <record name="r1"/>  </datasource> </field></definition>' % ( dsname[2], dsname[3], dsname[0] ) ) |
                        (gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition> <group type="NXentry"/> <field name="field1">  \n  <datasource name="%s" type="CLIENT">   <record name="r1"/>  </datasource> </field> <field name="field3">  <datasource name="%s" type="CLIENT">   <record name="r3"/>  </datasource> </field> <field name="field4">  \n  <datasource name="%s" type="CLIENT">   <record name="r4"/>  </datasource> </field></definition>' % ( dsname[0], dsname[2], dsname[3] ) )  )

        

      
        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 7)
        el.close()


    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_mixed(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()


        xds  = [
            '<datasource name="%s" type="CLIENT"><record name="r1" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r2" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r3" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r4" /></datasource>'
            ]


        odsname = "mcs_test_datasource"
        avds = el.availableDataSources()
        self.assertTrue(isinstance(avds, list))
        dsnp = len(xds)
        dsname = []
        for i in range(dsnp):
            
            dsname.append(odsname +'_%s' % i )
            while dsname[i] in avds:
                dsname[i] = dsname[i] + '_%s' %i

                
        for i in range(dsnp):
            self.setXML(el, xds[i] % dsname[i])
            self.assertEqual(el.storeDataSource(dsname[i]),None)
            print "DS store", dsname[i]
            self.__ds.append(dsname[i])

        print "AVAIL", el.availableDataSources()    




        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ['<definition><group type="NXentry"/><field name="field1">%s</field></definition>' % ("$datasources.%s" % dsname[0]),
               '<definition><group type="NXentry"/><field name="field2">%s</field></definition>' % ("$datasources.%s" % dsname[1]),
               '<definition><group type="NXentry"/><field name="field3">%s</field><field name="field4">%s</field></definition>' 
               % (xds[2] % dsname[2] ,"$datasources.%s" % dsname[3] )
               ]



        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])



        css = [name[0],name[2]]
        print "AVAIL2", el.availableDataSources()    

        gxml = el.merge(css) 
        self.assertTrue((gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition><group type="NXentry"/><field name="field3"><datasource name="%s" type="CLIENT"><record name="r3"/></datasource></field><field name="field4">$datasources.%s</field><field name="field1">$datasources.%s</field></definition>' % ( dsname[2], dsname[3], dsname[0] ) ) |
                        (gxml.replace("?>\n<","?><") ==  '<?xml version="1.0" ?><definition><group type="NXentry"/><field name="field1">$datasources.%s</field><field name="field3"><datasource name="%s" type="CLIENT"><record name="r3"/></datasource></field><field name="field4">$datasources.%s</field></definition>'% ( dsname[0], dsname[2], dsname[3] ) ))

        

      
        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 7)
        el.close()






    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_mixed_var(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()


        xds  = [
            '<datasource name="%s" type="CLIENT"><record name="$var.name1" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="$var.name2" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="$var.name3" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="$var.name4" /></datasource>'
            ]


        odsname = "mcs_test_datasource"
        avds = el.availableDataSources()
        self.assertTrue(isinstance(avds, list))
        dsnp = len(xds)
        dsname = []
        for i in range(dsnp):
            
            dsname.append(odsname +'_%s' % i )
            while dsname[i] in avds:
                dsname[i] = dsname[i] + '_%s' %i

                
        for i in range(dsnp):
            self.setXML(el, xds[i] % dsname[i])
            self.assertEqual(el.storeDataSource(dsname[i]),None)
            print "DS store", dsname[i]
            self.__ds.append(dsname[i])

        print "AVAIL", el.availableDataSources()    




        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ['<definition><group type="NXentry"/><field name="field1">%s</field></definition>' % ("$datasources.%s" % dsname[0]),
               '<definition><group type="NXentry"/><field name="field2">%s</field></definition>' % ("$datasources.%s" % dsname[1]),
               '<definition><group type="NXentry"/><field name="field3">%s</field><field name="field4">%s</field></definition>' 
               % (xds[2] % dsname[2] ,"$datasources.%s" % dsname[3] )
               ]



        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])



        css = [name[0],name[2]]
        print "AVAIL2", el.availableDataSources()    

        el.variables = '{"name1":"r1","name2":"r2","name3":"r3","name4":"r4"}'
        gxml = el.merge(css)
        self.assertTrue((gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition><group type="NXentry"/><field name="field3"><datasource name="%s" type="CLIENT"><record name="$var.name3"/></datasource></field><field name="field4">$datasources.%s</field><field name="field1">$datasources.%s</field></definition>' % ( dsname[2], dsname[3], dsname[0] ) ) |
                        (gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition><group type="NXentry"/><field name="field1">$datasources.%s</field><field name="field3"><datasource name="%s" type="CLIENT"><record name="$var.name3"/></datasource></field><field name="field4">$datasources.%s</field></definition>' % ( dsname[0], dsname[2], dsname[3] ) ))

        

      
        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 7)
        el.close()







    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_mixed_var_2(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()


        xds  = [
            '<datasource name="%s" type="CLIENT"><record name="$var.name1" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="$var.name2" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="$var.name3" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="$var.name5" /></datasource>'
            ]


        odsname = "mcs_test_datasource"
        avds = el.availableDataSources()
        self.assertTrue(isinstance(avds, list))
        dsnp = len(xds)
        dsname = []
        for i in range(dsnp):
            
            dsname.append(odsname +'_%s' % i )
            while dsname[i] in avds:
                dsname[i] = dsname[i] + '_%s' %i

                
        for i in range(dsnp):
            self.setXML(el, xds[i] % dsname[i])
            self.assertEqual(el.storeDataSource(dsname[i]),None)
            print "DS store", dsname[i]
            self.__ds.append(dsname[i])

        print "AVAIL", el.availableDataSources()    




        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ['<definition><group type="NXentry"/><field name="field1">%s</field></definition>' % ("$datasources.%s" % dsname[0]),
               '<definition><group type="NXentry"/><field name="field2">%s</field></definition>' % ("$datasources.%s" % dsname[1]),
               '<definition><group type="NXentry"/><field name="field3">%s</field><field name="field4">%s</field></definition>' 
               % (xds[2] % dsname[2] ,"$datasources.%s" % dsname[3] )
               ]



        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])



        css = [name[0],name[2]]
        print "AVAIL2", el.availableDataSources()    

        el.variables = '{"name1":"r1","name2":"r2","name3":"r3","name4":"r4"}'
        gxml = el.merge(css)
        self.assertTrue((gxml.replace("?>\n<","?><") =='<?xml version="1.0" ?><definition><group type="NXentry"/><field name="field3"><datasource name="%s" type="CLIENT"><record name="$var.name3"/></datasource></field><field name="field4">$datasources.%s</field><field name="field1">$datasources.%s</field></definition>' % ( dsname[2], dsname[3], dsname[0] )  ) | 
                         (gxml.replace("?>\n<","?><") =='<?xml version="1.0" ?><definition><group type="NXentry"/><field name="field1">$datasources.%s</field><field name="field3"><datasource name="%s" type="CLIENT"><record name="$var.name3"/></datasource></field><field name="field4">$datasources.%s</field></definition>' % ( dsname[0], dsname[2], dsname[3] )  ))

        

      
        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 7)
        el.close()








    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_mixed_2(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()


        xds  = [
            '<datasource name="%s" type="CLIENT"><record name="r1" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r2" /></datasource>'
            ]



        odsname = "mcs_test_datasource"
        avds = el.availableDataSources()
        self.assertTrue(isinstance(avds, list))
        dsnp = len(xds)
        dsname = []
        dsname.append(odsname +'_1')
        dsname.append(odsname +'_11')
        rename = odsname
        while dsname[0] in avds or dsname[1] in avds:
            rename = rename + "_1"
            dsname[0] = rename + '_1'
            dsname[1] = rename + '_11'
                
        for i in range(dsnp):
            self.setXML(el, xds[i] % dsname[i])
            self.assertEqual(el.storeDataSource(dsname[i]),None)
            print "DS store", dsname[i]
            self.__ds.append(dsname[i])

        print "AVAIL", el.availableDataSources()    




        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ['<definition><group type="NXentry"/><field name="field1">%s</field></definition>' % ("$datasources.%s" % dsname[0]),
               '<definition><group type="NXentry"/><field name="field2">%s</field></definition>' % ("$datasources.%s" % dsname[1]),
               '<definition><group type="NXentry"/><field name="field3">%s</field><field name="field4">%s</field></definition>' 
               % (xds[0] % dsname[0] ,"$datasources.%s" % dsname[1] ),
               '<definition><group type="NXentry"/><field name="field3">%s</field><field name="field4">%s</field></definition>' 
               % ("$datasources.%s" % dsname[0] ,"$datasources.%s" % dsname[1] )
               ]



        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])



        css = [name[0],name[2]]
        print "AVAIL2", el.availableDataSources()    

        gxml = el.merge(css)
        self.assertTrue((gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition><group type="NXentry"/><field name="field3"><datasource name="%s" type="CLIENT"><record name="r1"/></datasource></field><field name="field4">$datasources.%s</field><field name="field1">$datasources.%s</field></definition>' % (dsname[0],dsname[1],dsname[0])) |
                        (gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition><group type="NXentry"/><field name="field1">$datasources.%s</field><field name="field3"><datasource name="%s" type="CLIENT"><record name="r1"/></datasource></field><field name="field4">$datasources.%s</field></definition>' % (dsname[0],dsname[0],dsname[1])))

        

      
        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 6)
        el.close()





    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_mixed_2_double(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()


        xds  = [
            '<datasource name="%s" type="CLIENT"><record name="r1" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r2" /></datasource>'
            ]



        odsname = "mcs_test_datasource"
        avds = el.availableDataSources()
        self.assertTrue(isinstance(avds, list))
        dsnp = len(xds)
        dsname = []
        dsname.append(odsname +'_1')
        dsname.append(odsname +'_11')
        rename = odsname
        while dsname[0] in avds or dsname[1] in avds:
            rename = rename + "_1"
            dsname[0] = rename + '_1'
            dsname[1] = rename + '_11'
                
        for i in range(dsnp):
            self.setXML(el, xds[i] % dsname[i])
            self.assertEqual(el.storeDataSource(dsname[i]),None)
            print "DS store", dsname[i]
            self.__ds.append(dsname[i])

        print "AVAIL", el.availableDataSources()    




        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ['<definition><group type="NXentry"/><field name="field1">%s</field></definition>' % ("$datasources.%s" % dsname[0]),
               '<definition><group type="NXentry"/><field name="field2">%s</field></definition>' % ("$datasources.%s" % dsname[1]),
               '<definition><group type="NXentry"/><field name="field3">%s</field><field name="field4">%s</field></definition>' 
               % (xds[0] % dsname[0] ,"$datasources.%s" % dsname[1] ),
               '<definition><group type="NXentry"/><field name="field3"><datasource>%s%s</datasource></field></definition>' 
               % ("$datasources.%s" % dsname[0] ,"$datasources.%s" % dsname[1] )
               ]



        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])



        css = [name[0], name[3]]

        gxml = el.merge(css)
        self.assertTrue((gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition><group type="NXentry"/><field name="field3"><datasource>$datasources.%s$datasources.%s</datasource></field><field name="field1">$datasources.%s</field></definition>' % (dsname[0], dsname[1], dsname[0] )) |
                        (gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition><group type="NXentry"/><field name="field1">$datasources.%s</field><field name="field3"><datasource>$datasources.%s$datasources.%s</datasource></field></definition>' % (dsname[0], dsname[0], dsname[1] )) )

        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 6)
        el.close()





    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_mixed_3_double(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()


        xds  = [
            '<datasource name="%s" type="CLIENT"><record name="r1" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r2" /></datasource>',
            """<datasource name="%s" type="CLIENT">$datasources.%s$datasources.%s<result>
import ndts
ds.result = ndts.version</result></datasource>"""
            ]



        odsname = "mcs_test_datasource"
        avds = el.availableDataSources()
        self.assertTrue(isinstance(avds, list))
        dsnp = len(xds)
        dsname = []
        dsname.append(odsname +'_1')
        dsname.append(odsname +'_11')
        dsname.append(odsname +'_111')
        rename = odsname
        while dsname[0] in avds or dsname[1] in avds or dsname[2] in avds:
            rename = rename + "_1"
            dsname[0] = rename + '_1'
            dsname[1] = rename + '_11'
            dsname[2] = rename + '_111'
                
        for i in range(dsnp):
            if i < 2:
                self.setXML(el, xds[i] % dsname[i])
            else:
                self.setXML(el, xds[i] % (dsname[2], dsname[0], dsname[1]))
            self.assertEqual(el.storeDataSource(dsname[i]),None)
            print "DS store", dsname[i]
            self.__ds.append(dsname[i])

        print "AVAIL", el.availableDataSources()    




        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ['<definition><group type="NXentry"/><field name="field1">%s</field></definition>' % ("$datasources.%s" % dsname[0]),
               '<definition><group type="NXentry"/><field name="field2">%s</field></definition>' % ("$datasources.%s" % dsname[1]),
               '<definition><group type="NXentry"/><field name="field3">%s</field><field name="field4">%s</field></definition>' 
               % (xds[0] % dsname[0] ,"$datasources.%s" % dsname[1] ),
               '<definition><group type="NXentry"/><field name="field3">%s</field></definition>' 
               % ("$datasources.%s" % dsname[2] )
               ]



        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i])
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])



        css = [name[0], name[3]]
        print "AVAIL2", el.availableDataSources()    

        gxml = el.merge(css)
        mxml = gxml.replace(">    ",">").replace(">   ",">").replace(">  ",">").replace("> ",">")\
                .replace("    <","<").replace("   <","<").replace("  <","<").replace(" <","<")\
                .replace("?>\n<","?><")   
        
        self.assertTrue((mxml  == '<?xml version="1.0" ?><definition><group type="NXentry"/><field name="field3">$datasources.%s</field><field name="field1">$datasources.%s</field></definition>' % (dsname[2],  dsname[0])) |
                        (mxml  == '<?xml version="1.0" ?><definition><group type="NXentry"/><field name="field1">$datasources.%s</field><field name="field3">$datasources.%s</field></definition>' % (dsname[0],  dsname[2])))
        
        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 7)
        el.close()




    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_merge_mixed_definition(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        el = self.openConfig(self.__args)
        man = el.mandatoryComponents()
        el.unsetMandatoryComponents(man)
        self.__man += man


        avc = el.availableComponents()


        xds  = [
            '<datasource name="%s" type="CLIENT"><record name="r1" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r2" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r3" /></datasource>',
            '<datasource name="%s" type="CLIENT"><record name="r4" /></datasource>'
            ]
 

        odsname = "mcs_test_datasource"
        avds = el.availableDataSources()
        self.assertTrue(isinstance(avds, list))
        dsnp = len(xds)
        dsname = []
        for i in range(dsnp):
            
            dsname.append(odsname +'_%s' % i )
            while dsname[i] in avds:
                dsname[i] = dsname[i] + '_%s' %i

                
        for i in range(dsnp):
            self.setXML(el, "<?xml version=\'1.0\'?><definition>%s</definition>" % (xds[i] % dsname[i]))
            self.assertEqual(el.storeDataSource(dsname[i]),None)
            self.__ds.append(dsname[i])




        oname = "mcs_test_component"
        self.assertTrue(isinstance(avc, list))
        xml = ['<definition><group type="NXentry"/><field name="field1">%s</field></definition>' % ("$datasources.%s" % dsname[0]),
               '<definition><group type="NXentry"/><field name="field2">%s</field></definition>' % ("$datasources.%s" % dsname[1]),
               '<definition><group type="NXentry"/><field name="field3">%s</field><field name="field4">%s</field></definition>' 
               % (xds[2] % dsname[2] ,"$datasources.%s" % dsname[3] )
               ]



        np = len(xml)
        name = []
        for i in range(np):
            
            name.append(oname +'_%s' % i )
            while name[i] in avc:
                name[i] = name[i] + '_%s' %i
#        print avc

        for i in range(np):
            self.setXML(el, xml[i] )
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])



        css = [name[0],name[2]]
        print el.components([name[0],name[2]])
        print "CSS",css
        print "MAND", el.mandatoryComponents()
        gxml = el.merge(css)
        self.assertTrue((gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition><group type="NXentry"/><field name="field3"><datasource name="%s" type="CLIENT"><record name="r3"/></datasource></field><field name="field4">$datasources.%s</field><field name="field1">$datasources.%s</field></definition>' % ( dsname[2], dsname[3], dsname[0] ) ) |
                        (gxml.replace("?>\n<","?><") == '<?xml version="1.0" ?><definition><group type="NXentry"/><field name="field1">$datasources.%s</field><field name="field3"><datasource name="%s" type="CLIENT"><record name="r3"/></datasource></field><field name="field4">$datasources.%s</field></definition>' % ( dsname[0], dsname[2], dsname[3] ) ))

        

      
        

        el.setMandatoryComponents(man)
        self.assertEqual(long(el.version.split('.')[-1]),self.revision + 7)
        el.close()




if __name__ == '__main__':
    unittest.main()
