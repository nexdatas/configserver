#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012 Jan Kotanski
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
## \package mcs nexdatas.configserver
## \file MYSQLDataBase.py
# Allows the access to MYSQL database with NDTS configuration files 
#

import MySQLdb


## XML Configurer
class MYSQLDataBase(object):
    def __init__(self):
        ## XML string
        self.xmlConfig = ""
        self.db = None 

    def connect(self, args):
        print "connect:", args
        self.db = MySQLdb.connect(**args)


    def close(self):
        self.db.close()


    def components(self, argin): 
        argout = []
        if self.db is not None:
            try:
                cursor = self.db.cursor()
                for ar in argin:
                    cursor.execute("select xml from components where name = '%s';" % ar)
                    data=cursor.fetchone()
                    argout.append(data[0])
                cursor.close()    
            except:
                cursor.close()    
                raise
        print "components"
        return argout


    def dataSources(self, argin):
        argout = []
        if self.db is not None:
            try:
                cursor = self.db.cursor()
                for ar in argin:
                    cursor.execute("select xml from datasources where name = '%s';" % ar)
                    data=cursor.fetchone()
                    argout.append(data[0])
                cursor.close()    
            except:
                cursor.close()    
                raise
#        print "dataSources"
        return argout



    def availableComponents(self):
        argout = []
        if self.db is not None:
            try:
                cursor = self.db.cursor()
                cursor.execute("select name from components;")
                data=cursor.fetchall()
                argout = [d[0] for d in data]
                cursor.close()    
            except:
                cursor.close()    
                raise

#        print "available components"
        return argout



    def availableDataSources(self):
        argout = []
        if self.db is not None:
            try:
                cursor = self.db.cursor()
                cursor.execute("select name from datasources;")
                data=cursor.fetchall()
                argout = [d[0] for d in data]
                cursor.close()    
            except:
                cursor.close()    
                raise
#        print "available datasources"
        return argout


    def storeComponent(self, name, xml):
        if self.db is not None:
            try:
                cursor = self.db.cursor()
                cursor.execute("select exists(select 1 from components where name = '%s');" % name)
                data=cursor.fetchone()
                if data[0]:
                    cursor.execute("update components set xml = '%s' where name = '%s';" 
                                   % (name, xml))
                else:
                    cursor.execute("insert into components values('%s','%s');" 
                                   % (name, xml))
                    
                self.db.commit()
                cursor.close()    
            except:
                self.db.rollback()
                cursor.close()    
                raise
    

            print "store component", name


    def storeDataSource(self, name, xml):
        if self.db is not None:
            try:
                cursor = self.db.cursor()
                cursor.execute("select exists(select 1 from datasources where name = '%s');" % name)
                data=cursor.fetchone()
                if data[0]:
                    cursor.execute("update datasources set xml = '%s' where name = '%s';" 
                                   % (name, xml))
                else:
                    cursor.execute("insert into datasources values('%s','%s');" 
                                   % (name, xml))
                    
                self.db.commit()
                cursor.close()    
            except:
                self.db.rollback()
                cursor.close()    
                raise
            print "store DataSource", name


    def deleteComponent(self, name):
        if self.db is not None:
            try:
                cursor = self.db.cursor()
                cursor.execute("select exists(select 1 from components where name = '%s');" % name)
                data=cursor.fetchone()
                if data[0]:
                    cursor.execute("delete from components where name = '%s';" % name)
                    
                    self.db.commit()
                cursor.close()    
            except:
                self.db.rollback()
                cursor.close()    
                raise
    

            print "store component", name


    def deleteDataSource(self, name):
        if self.db is not None:
            try:
                cursor = self.db.cursor()
                cursor.execute("select exists(select 1 from datasources where name = '%s');" % name)
                data=cursor.fetchone()
                if data[0]:
                    cursor.execute("delete from datasources where name = '%s';" % name)
                    
                    self.db.commit()
                cursor.close()    
            except:
                self.db.rollback()
                cursor.close()    
                raise
            print "store DataSource", name


if __name__ == "__main__":

    import time

            
                
    
