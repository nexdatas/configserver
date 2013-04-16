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


from ndtsconfigserver.XMLConfigurator  import XMLConfigurator
from ndtsconfigserver.Merger import Merger
from ndtsconfigserver.Errors import NonregisteredDBRecordError, UndefinedTagError, IncompatibleNodeError

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
        except exception, e:
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
        return xmlc

    ## closes configurator
    # \param xmlc XMLConfigurator instance   
    def closeConfig(self, xmlc):
        xmlc.close()

    ## open close test test
    # \brief It tests XMLConfigurator
    def test_openClose(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        
        xmlc = self.openConfig(self.__args)
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
        el.xmlConfig = xml
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
        el.xmlConfig = xml
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

        el.xmlConfig = xml
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



        el.xmlConfig = xml2
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

        el.xmlConfig = xml
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


        el.xmlConfig = xml2
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
        el.xmlConfig = xml
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
        el.xmlConfig = xml
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

        el.xmlConfig = xml
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



        el.xmlConfig = xml2
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

        el.xmlConfig = xml
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


        el.xmlConfig = xml2
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
        el.xmlConfig = xml
        self.assertEqual(el.storeComponent(name),None)
        self.__cmps.append(name)

#        print man
        self.assertEqual(el.setMandatoryComponents([name]), None)
        man2 = el.mandatoryComponents()
        self.assertEqual(len(man)+1,len(man2))
        for cp in man:
            self.assertTrue(cp in man2)
            
        self.assertTrue(name in man2)

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


        el.xmlConfig = xml
        self.assertEqual(el.storeComponent(name),None)
        self.__cmps.append(name)

#        print man
        self.assertEqual(el.setMandatoryComponents([name]), None)
        man2 = el.mandatoryComponents()
        self.assertEqual(len(man)+1,len(man2))
        for cp in man:
            self.assertTrue(cp in man2)
            
        self.assertTrue(name in man2)

        el.xmlConfig = xml
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

        self.assertEqual(el.createConfiguration([]), None)
        self.assertEqual(el.xmlConfig, None)
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
        el.xmlConfig = xml
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
        self.assertEqual(el.xmlConfig.replace("?>\n<","?><"),'<?xml version="1.0" ?><definition> <group type="NXentry"/></definition>')

        self.assertEqual(el.deleteComponent(name),None)
        self.__cmps.pop()
        
        avc3 = el.availableComponents()
        self.assertTrue(isinstance(avc3, list))
        for cp in avc:
            self.assertTrue(cp in avc3)
        self.assertTrue(name not in avc3)


        el.setMandatoryComponents(man)
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
        el.xmlConfig = xml
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
        el.xmlConfig = xml[0]
        self.assertEqual(el.storeComponent(name[0]),None)
        self.__cmps.append(name[0])

        el.xmlConfig = xml[1]
        self.assertEqual(el.storeComponent(name[1]),None)
        self.__cmps.append(name[1])

        
        self.assertEqual(el.createConfiguration(name), None)
        self.assertEqual(el.xmlConfig.replace("?>\n<","?><"),'<?xml version="1.0" ?><definition> <group type="NXentry"/></definition>')

        self.assertEqual(el.deleteComponent(name[1]),None)
        self.__cmps.pop()

        self.assertEqual(el.deleteComponent(name[0]),None)
        self.__cmps.pop()
        

        el.setMandatoryComponents(man)
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
            el.xmlConfig = xml[i]
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        self.assertEqual(el.createConfiguration(name), None)
        self.assertEqual(el.xmlConfig.replace("?>\n<","?><"),'<?xml version="1.0" ?><definition> <group type="NXentry"/></definition>')

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
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
            el.xmlConfig = xml[i]
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        self.assertEqual(el.createConfiguration(name), None)
        self.assertEqual(el.xmlConfig.replace("?>\n<","?><"),'<?xml version="1.0" ?><definition> <group type="NXentry2"/> <group type="NXentry"/></definition>')

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
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
            el.xmlConfig = xml[i]
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
            el.xmlConfig = xml[i]
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
            el.xmlConfig = xml[i]
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        self.assertEqual(el.createConfiguration(name), None)
        self.assertEqual(el.xmlConfig.replace("?>\n<","?><"),'<?xml version="1.0" ?><definition> <group type="NXentry">  <field type="field"/> </group></definition>')

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
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
            el.xmlConfig = xml[i]
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        self.assertEqual(el.createConfiguration(name), None)
        self.assertEqual(el.xmlConfig.replace("?>\n<","?><"),'<?xml version="1.0" ?><definition> <group type="NXentry2"/> <field name="field1"/> <group type="NXentry">  <field name="field1"/> </group></definition>' )

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
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
            el.xmlConfig = xml[i]
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        self.assertEqual(el.createConfiguration(name), None)
        self.assertEqual(el.xmlConfig.replace("?>\n<","?><"),'<?xml version="1.0" ?><definition> <group name="entry" type="NXentry2"/></definition>')

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
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
            el.xmlConfig = xml[i]
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        self.assertEqual(el.createConfiguration(name), None)
        self.assertEqual(el.xmlConfig.replace("?>\n<","?><"),'<?xml version="1.0" ?><definition> <group name="entry" type="NXentry"/></definition>')

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
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
            el.xmlConfig = xml[i]
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        self.assertEqual(el.createConfiguration(name), None)
        self.assertEqual(el.xmlConfig.replace("?>\n<","?><"), '<?xml version="1.0" ?><definition> <group name="entry" type="NXentry"/> <group name="entry2"/></definition>')

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
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
            el.xmlConfig = xml[i]
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        self.assertEqual(el.createConfiguration(name), None)
        self.assertEqual(el.xmlConfig.replace("?>\n<","?><"), '<?xml version="1.0" ?><definition> <group type="NXentry">  <field type="field"/> </group></definition>')

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
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
            el.xmlConfig = xml[i]
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        self.assertEqual(el.createConfiguration(name), None)
        self.assertEqual(el.xmlConfig.replace("?>\n<","?><"), '<?xml version="1.0" ?><definition> <group name="entry" type="NXentry">  <field type="field"/> </group></definition>' )

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
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
            el.xmlConfig = xml[i]
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        self.myAssertRaise(IncompatibleNodeError,el.createConfiguration, name)
         
        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
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
            el.xmlConfig = xml[i]
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        
        self.assertEqual(el.createConfiguration(name), None)
        self.assertEqual(el.xmlConfig.replace("?>\n<","?><"), '<?xml version="1.0" ?><definition> <group name="entry2" type="NXentry2">  <field type="field"/> </group> <group name="entry" type="NXentry">  <field type="field"/> </group></definition>' )

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
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
                el.xmlConfig = xml[i]
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])

        
            self.myAssertRaise(IncompatibleNodeError,el.createConfiguration,name)


            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
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
                el.xmlConfig = xml[i]
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])

        
            self.myAssertRaise(IncompatibleNodeError,el.createConfiguration,name)

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
        el.close()






    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConf_children_datasource(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = Merger()
        uts = el.children['datasource']
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
                el.xmlConfig = xml[i]
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            self.assertEqual(el.createConfiguration(name), None)
            self.assertEqual(el.xmlConfig.replace("?>\n<","?><"),  '<?xml version="1.0" ?><definition> <field name="entry">  <datasource type="TANGO">   <%s/>  </datasource> </field></definition>' % (ut) )

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
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
                if w not in  el.children["datasource"]:
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
                el.xmlConfig = xml[i]
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            self.myAssertRaise(IncompatibleNodeError,el.createConfiguration,name)

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
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
                el.xmlConfig = xml[i]
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            self.assertEqual(el.createConfiguration(name), None)
            self.assertEqual(el.xmlConfig.replace("?>\n<","?><"),  '<?xml version="1.0" ?><definition> <field name="entry">  <attribute type="TANGO">   <%s/>  </attribute> </field></definition>' % (ut) )

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
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
                el.xmlConfig = xml[i]
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            self.myAssertRaise(IncompatibleNodeError,el.createConfiguration, name)

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
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
                el.xmlConfig = xml[i]
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            self.assertEqual(el.createConfiguration(name), None)
            self.assertEqual(el.xmlConfig.replace("?>\n<","?><"),  '<?xml version="1.0" ?><definition> <%s name="entry"/></definition>' % (ut) )

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
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
                el.xmlConfig = xml[i]
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            self.myAssertRaise(IncompatibleNodeError,el.createConfiguration, name)

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
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
                el.xmlConfig = xml[i]
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            self.assertEqual(el.createConfiguration(name), None)
            self.assertEqual(el.xmlConfig.replace("?>\n<","?><"),'<?xml version="1.0" ?><definition> <field name="entry">  <dimensions type="TANGO">   <%s/>  </dimensions> </field></definition>' % (ut) )

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
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
                el.xmlConfig = xml[i]
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            print i    
            self.myAssertRaise(IncompatibleNodeError,el.createConfiguration,name)

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
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
                el.xmlConfig = xml[i]
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            self.assertEqual(el.createConfiguration(name), None)
            self.assertEqual(el.xmlConfig.replace("?>\n<","?><"),'<?xml version="1.0" ?><definition> <field name="entry">  <%s/> </field></definition>' % (ut) )

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
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
                el.xmlConfig = xml[i]
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            self.myAssertRaise(IncompatibleNodeError,el.createConfiguration,name)

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
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
                el.xmlConfig = xml[i]
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            self.assertEqual(el.createConfiguration(name), None)
            self.assertEqual(el.xmlConfig.replace("?>\n<","?><"),'<?xml version="1.0" ?><definition> <group name="entry">  <%s/> </group></definition>' % (ut) )

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
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
                el.xmlConfig = xml[i]
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])

            self.myAssertRaise(IncompatibleNodeError,el.createConfiguration,name)


            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
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
                el.xmlConfig = xml[i]
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            self.assertEqual(el.createConfiguration(name), None)
            self.assertEqual(el.xmlConfig.replace("?>\n<","?><"),
                             '<?xml version="1.0" ?><definition> <link name="entry">  <%s/> </link></definition>' % (ut) )

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
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
                el.xmlConfig = xml[i]
                self.assertEqual(el.storeComponent(name[i]),None)
                self.__cmps.append(name[i])


            self.myAssertRaise(IncompatibleNodeError,el.createConfiguration,name)

            for i in range(np):
                self.assertEqual(el.deleteComponent(name[i]),None)
                self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
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
            el.xmlConfig = xml[i]
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        el.setMandatoryComponents([name[0]])
        self.assertEqual(el.mandatoryComponents(),[name[0]])
        

        self.assertEqual(el.createConfiguration([name[1]]), None)
        self.assertEqual(el.xmlConfig.replace("?>\n<","?><"),'<?xml version="1.0" ?><definition> <group type="NXentry2"/> <group type="NXentry"/></definition>')

        el.unsetMandatoryComponents([name[0]])
        self.assertEqual(el.mandatoryComponents(),[])

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        

        el.setMandatoryComponents(man)
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
            el.xmlConfig = xml[i]
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])

        el.setMandatoryComponents([name[0],name[1]])
        self.assertEqual(el.mandatoryComponents().sort(),[name[0],name[1]].sort())

        
        self.assertEqual(el.createConfiguration([name[2]]), None)
        self.assertTrue( 
            (el.xmlConfig.replace("?>\n<","?><") ==  '<?xml version="1.0" ?><definition> <group type="NXentry2"/> <group type="NXentry3"/> <group type="NXentry"/></definition>') | 
            (el.xmlConfig.replace("?>\n<","?><") ==  '<?xml version="1.0" ?><definition> <group type="NXentry3"/> <group type="NXentry2"/> <group type="NXentry"/></definition>') |
            (el.xmlConfig.replace("?>\n<","?><") ==  '<?xml version="1.0" ?><definition> <group type="NXentry3"/> <group type="NXentry"/> <group type="NXentry2"/></definition>') |
            (el.xmlConfig.replace("?>\n<","?><") ==  '<?xml version="1.0" ?><definition> <group type="NXentry2"/> <group type="NXentry"/> <group type="NXentry3"/></definition>') |
            (el.xmlConfig.replace("?>\n<","?><") ==  '<?xml version="1.0" ?><definition> <group type="NXentry"/> <group type="NXentry2"/> <group type="NXentry3"/></definition>') |
            (el.xmlConfig.replace("?>\n<","?><") ==  '<?xml version="1.0" ?><definition> <group type="NXentry"/> <group type="NXentry3"/> <group type="NXentry2"/></definition>') 
                         )
        

        el.unsetMandatoryComponents([name[1]])


        self.assertEqual(el.mandatoryComponents(),[name[0]])

        for i in range(np):
            self.assertEqual(el.deleteComponent(name[i]),None)
            self.__cmps.pop(0)

        self.assertEqual(el.mandatoryComponents(),[])
        

        el.setMandatoryComponents(man)
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
            el.xmlConfig = xds[i] % dsname[i]
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
            el.xmlConfig = xml[i]
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])



        css = [name[0],name[2]]
        cmps = []
        for cs in css:
            mdss = el.componentDataSources(cs)
            cmps.extend(mdss)
        self.assertEqual(cmps,[dsname[0],dsname[2],dsname[3]])
        
        

        el.setMandatoryComponents(man)
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
            el.xmlConfig = xds[i] % dsname[i]
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
            el.xmlConfig = xml[i]
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])



        css = [name[0],name[2]]
        cmps = []
        for cs in css:
            mdss = el.componentDataSources(cs)
            cmps.extend(mdss)
        self.assertEqual(cmps,[dsname[0],dsname[2],dsname[3]])
        
        

        el.setMandatoryComponents(man)
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
            el.xmlConfig = xds[i] % dsname[i]
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
            el.xmlConfig = xml[i]
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
        el.close()






    ## creatConf test
    # \brief It tests XMLConfigurator
    def test_createConfiguraton_mixed(self):
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
            el.xmlConfig = xds[i] % dsname[i]
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
            el.xmlConfig = xml[i] 
            self.assertEqual(el.storeComponent(name[i]),None)
            self.__cmps.append(name[i])



        css = [name[0],name[2]]

        self.assertEqual(el.createConfiguration(css), None)
        self.assertEqual(el.xmlConfig.replace("?>\n<","?><"),'<?xml version="1.0" ?><definition> <group type="NXentry"/> <field name="field3">  <datasource name="%s" type="CLIENT">   <record name="r3"/>  </datasource> </field> <field name="field4">  \n  <datasource name="%s" type="CLIENT">   <record name="r4"/>  </datasource> </field> <field name="field1">  \n  <datasource name="%s" type="CLIENT">   <record name="r1"/>  </datasource> </field></definition>' % ( dsname[2], dsname[3], dsname[0] ) )

        

      
        

        el.setMandatoryComponents(man)
        el.close()




if __name__ == '__main__':
    unittest.main()
