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
## \file MYSQLDataBaseTest.py
# unittests for Error classes
#
import unittest
import os
import sys
import subprocess
import random
import struct
import numpy



from ndtsconfigserver.MYSQLDataBase import MYSQLDataBase
from ndtsconfigserver.Errors import NonregisteredDBRecordError                         

## test fixture
class MYSQLDataBaseTest(unittest.TestCase):

    ## constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self.__args = {'host': u'localhost', 'db': u'ndts', 'read_default_file': u'/etc/my.cnf', 'use_unicode': True}
        self.__cmps = []
        self.__ds = []

    ## test starter
    # \brief Common set up
    def setUp(self):
        ## file handle
        print "\nsetting up..."        

    ## test closer
    # \brief Common tear down
    def tearDown(self):
        print "tearing down ..."
        if self.__cmps:
            el = MYSQLDataBase()
            el.connect(self.__args)
            for cp in self.__cmps:
                el.deleteComponent(cp)
            el.close()
        if self.__ds:
            el = MYSQLDataBase()
            el.connect(self.__args)
            for ds in self.__ds:
                el.deleteDataSource(ds)
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


    ##  constructor test
    # \brief It tests default settings
    def test_init(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = MYSQLDataBase()
        self.assertTrue(isinstance(el, object))



    ##  constructor test
    # \brief It tests default settings
    def test_connect_close(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = MYSQLDataBase()
        self.assertTrue(isinstance(el, object))
        self.assertEqual(el.connect(self.__args),None)
        self.assertEqual(el.close(),None)


    ##  component test
    # \brief It tests default settings
    def test_available_comp(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = MYSQLDataBase()
        self.assertTrue(isinstance(el, object))
        self.assertEqual(el.connect(self.__args),None)
        avc = el.availableComponents()
        self.assertTrue(isinstance(avc, list))
        name = "mcs_test_component"
        xml = "<?xml version='1.0'?><definition><group type='NXentry'/></definition>"
        while name in avc:
            name = name + '_1'
#        print avc
        self.assertEqual(el.storeComponent(name, xml),None)
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
        
        self.assertEqual(el.close(),None)


    ##  component test
    # \brief It tests default settings
    def test_available_comp_xml(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = MYSQLDataBase()
        self.assertTrue(isinstance(el, object))
        self.assertEqual(el.connect(self.__args),None)
        avc = el.availableComponents()
        self.assertTrue(isinstance(avc, list))
        name = "mcs_test_component"
        xml = "<?xml version='1.0'?><definition><group type='NXentry'/></definition>"
        while name in avc:
            name = name + '_1'
#        print avc
        cpx = el.components(avc)
        self.assertEqual(el.storeComponent(name, xml),None)
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
        el = MYSQLDataBase()
        self.assertTrue(isinstance(el, object))
        self.assertEqual(el.connect(self.__args),None)
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
        el = MYSQLDataBase()
        self.assertTrue(isinstance(el, object))
        self.assertEqual(el.connect(self.__args),None)
        avc = el.availableComponents()
        self.assertTrue(isinstance(avc, list))
        name = "mcs_test_component"
        xml = "<?xml version='1.0'?><definition><group type='NXentry'/></definition>"
        xml2 = "<?xml version='1.0'?><definition><group type='NXentry2'/></definition>"
        while name in avc:
            name = name + '_1'
#        print avc
        cpx = el.components(avc)

        self.assertEqual(el.storeComponent(name, xml),None)
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



        self.assertEqual(el.storeComponent(name, xml2),None)
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
    def test_available_comp2_xml(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = MYSQLDataBase()
        self.assertTrue(isinstance(el, object))
        self.assertEqual(el.connect(self.__args),None)
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

        self.assertEqual(el.storeComponent(name, xml),None)
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


        self.assertEqual(el.storeComponent(name2, xml2),None)
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





    ##  datasource test
    # \brief It tests default settings
    def test_available_dsrc(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = MYSQLDataBase()
        self.assertTrue(isinstance(el, object))
        self.assertEqual(el.connect(self.__args),None)
        avc = el.availableDataSources()
        self.assertTrue(isinstance(avc, list))
        name = "mcs_test_datasource"
        xml = "<?xml version='1.0'?><definition><group type='NXentry'/></definition>"
        while name in avc:
            name = name + '_1'
#        print avc
        self.assertEqual(el.storeDataSource(name, xml),None)
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
        
        self.assertEqual(el.close(),None)


    ##  datasource test
    # \brief It tests default settings
    def test_available_dsrc_xml(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = MYSQLDataBase()
        self.assertTrue(isinstance(el, object))
        self.assertEqual(el.connect(self.__args),None)
        avc = el.availableDataSources()
        self.assertTrue(isinstance(avc, list))
        name = "mcs_test_datasource"
        xml = "<?xml version='1.0'?><definition><group type='NXentry'/></definition>"
        while name in avc:
            name = name + '_1'
#        print avc
        cpx = el.dataSources(avc)
        self.assertEqual(el.storeDataSource(name, xml),None)
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


    ##  datasource test
    # \brief It tests default settings
    def test_available_no_dsrc(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = MYSQLDataBase()
        self.assertTrue(isinstance(el, object))
        self.assertEqual(el.connect(self.__args),None)
        avc = el.availableDataSources()
        self.assertTrue(isinstance(avc, list))
        name = "mcs_test_datasource"
        xml = "<?xml version='1.0'?><definition><group type='NXentry'/></definition>"
        while name in avc:
            name = name + '_1'
#        print avc
        self.myAssertRaise(NonregisteredDBRecordError,el.dataSources, [name])
        
        self.assertEqual(el.close(),None)




    ##  datasource test
    # \brief It tests default settings
    def test_available_dsrc_update(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = MYSQLDataBase()
        self.assertTrue(isinstance(el, object))
        self.assertEqual(el.connect(self.__args),None)
        avc = el.availableDataSources()
        self.assertTrue(isinstance(avc, list))
        name = "mcs_test_datasource"
        xml = "<?xml version='1.0'?><definition><group type='NXentry'/></definition>"
        xml2 = "<?xml version='1.0'?><definition><group type='NXentry2'/></definition>"
        while name in avc:
            name = name + '_1'
#        print avc
        cpx = el.dataSources(avc)

        self.assertEqual(el.storeDataSource(name, xml),None)
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



        self.assertEqual(el.storeDataSource(name, xml2),None)
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





    ##  datasource test
    # \brief It tests default settings
    def test_available_dsrc2_xml(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        el = MYSQLDataBase()
        self.assertTrue(isinstance(el, object))
        self.assertEqual(el.connect(self.__args),None)
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

        self.assertEqual(el.storeDataSource(name, xml),None)
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


        self.assertEqual(el.storeDataSource(name2, xml2),None)
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
        el = MYSQLDataBase()
        self.assertTrue(isinstance(el, object))
        self.assertEqual(el.connect(self.__args),None)
        man = el.mandatory()
        self.assertTrue(isinstance(man, list))
        avc = el.availableComponents()
        
        name = "mcs_test_component"
        xml = "<?xml version='1.0'?><definition><group type='NXentry'/></definition>"
        while name in avc:
            name = name + '_1'
#        print avc

        self.assertEqual(el.setMandatory(name), None)
        man2 = el.mandatory()
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
        el = MYSQLDataBase()
        self.assertTrue(isinstance(el, object))
        self.assertEqual(el.connect(self.__args),None)
        man = el.mandatory()
        self.assertTrue(isinstance(man, list))
        avc = el.availableComponents()
        
        name = "mcs_test_component"
        xml = "<?xml version='1.0'?><definition><group type='NXentry'/></definition>"
        while name in avc:
            name = name + '_1'
#        print avc
        self.assertEqual(el.storeComponent(name, xml),None)
        self.__cmps.append(name)

#        print man
        self.assertEqual(el.setMandatory(name), None)
        man2 = el.mandatory()
        self.assertEqual(len(man)+1,len(man2))
        for cp in man:
            self.assertTrue(cp in man2)
            
        self.assertTrue(name in man2)

        self.assertEqual(el.unsetMandatory(name), None)

        man2 = el.mandatory()
        self.assertEqual(len(man),len(man2))
        for cp in man:
            self.assertTrue(cp in man2)
            
        self.assertTrue(not name in man2)

        self.assertEqual(el.deleteComponent(name), None)
        self.__cmps.pop()

        man2 = el.mandatory()
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
        el = MYSQLDataBase()
        self.assertTrue(isinstance(el, object))
        self.assertEqual(el.connect(self.__args),None)
        man = el.mandatory()
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


        self.assertEqual(el.storeComponent(name, xml),None)
        self.__cmps.append(name)

#        print man
        self.assertEqual(el.setMandatory(name), None)
        man2 = el.mandatory()
        self.assertEqual(len(man)+1,len(man2))
        for cp in man:
            self.assertTrue(cp in man2)
            
        self.assertTrue(name in man2)

        self.assertEqual(el.storeComponent(name2, xml),None)
        self.__cmps.append(name2)

#        print man
        self.assertEqual(el.setMandatory(name2), None)
        man2 = el.mandatory()
        self.assertEqual(len(man)+2,len(man2))
        for cp in man:
            self.assertTrue(cp in man2)
            
        self.assertTrue(name in man2)
        self.assertTrue(name2 in man2)

        self.assertEqual(el.unsetMandatory(name), None)


#        print man
        man2 = el.mandatory()
        self.assertEqual(len(man)+1,len(man2))
        for cp in man:
            self.assertTrue(cp in man2)
            
        self.assertTrue(name2 in man2)


        self.assertEqual(el.unsetMandatory(name2), None)

        man2 = el.mandatory()
        self.assertEqual(len(man),len(man2))
        for cp in man:
            self.assertTrue(cp in man2)
            
        self.assertTrue(not name in man2)

        self.assertEqual(el.deleteComponent(name), None)
        self.__cmps.pop()
        self.assertEqual(el.deleteComponent(name2), None)
        self.__cmps.pop()

        man2 = el.mandatory()
        self.assertEqual(len(man),len(man2))
        for cp in man:
            self.assertTrue(cp in man2)
            
        self.assertTrue(not name in man2)
            

        self.assertEqual(el.close(), None)


if __name__ == '__main__':
    unittest.main()
