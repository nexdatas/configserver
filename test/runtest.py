#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2016 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
## \file runtest.py
# the unittest runner
#

import os
import unittest

import ComponentHandlerTest
import MergerTest
import ErrorsTest
import StreamsTest

try:
    import PyTango
    ## if module PyTango avalable
    PYTANGO_AVAILABLE = True
except ImportError, e:
    PYTANGO_AVAILABLE = False
    print "PyTango is not available: %s" % e

## list of available databases
DB_AVAILABLE = []

try:
    import MySQLdb
    ## connection arguments to MYSQL DB
    args = {'host': u'localhost', 'db': u'nxsconfig',
            'read_default_file': u'/etc/my.cnf', 'use_unicode': True}
    ## inscance of MySQLdb
    mydb = MySQLdb.connect(**args)
    mydb.close()
    DB_AVAILABLE.append("MYSQL")
except:
    try:
        import MySQLdb
        from os.path import expanduser
        home = expanduser("~")
        ## connection arguments to MYSQL DB
        args2 = {'host': u'localhost', 'db': u'nxsconfig',
                 'read_default_file': u'%s/.my.cnf' % home,
                 'use_unicode': True}
        ## inscance of MySQLdb
        mydb = MySQLdb.connect(**args2)
        mydb.close()
        DB_AVAILABLE.append("MYSQL")

    except ImportError, e:
        print "MYSQL not available: %s" % e
    except Exception, e:
        print "MYSQL not available: %s" % e
    except:
        print "MYSQL not available"


if "MYSQL" in DB_AVAILABLE:
    import MYSQLDataBaseTest
    import XMLConfiguratorTest


if PYTANGO_AVAILABLE:
    if "MYSQL" in DB_AVAILABLE:
        import NXSConfigServerTest


#import TestServerSetUp

## main function
def main():

    ## test server
    ts = None

    ## test suit
    suite = unittest.TestSuite()

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(ComponentHandlerTest))

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(MergerTest))

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(ErrorsTest))

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(StreamsTest))

    if "MYSQL" in DB_AVAILABLE:
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(MYSQLDataBaseTest))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(
                XMLConfiguratorTest))

    if PYTANGO_AVAILABLE:

        if "MYSQL" in DB_AVAILABLE:
            suite.addTests(
                unittest.defaultTestLoader.loadTestsFromModule(
                    NXSConfigServerTest))

    ## test runner
    runner = unittest.TextTestRunner()
    ## test result
    result = runner.run(suite)


if __name__ == "__main__":
    main()
