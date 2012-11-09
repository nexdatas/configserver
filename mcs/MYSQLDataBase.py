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

##  Error for non-existing database records
class NonregisteredDBRecordError(Exception): 
    pass


## XML Configurer
class MYSQLDataBase(object):
    ## constructor
    # \brief It sets xmlConfig to null string
    def __init__(self):
        ## XML string
        self.xmlConfig = ""
        self._db = None 

    ## connects to the database
    # \param args arguments of the MySQLdb connect method    
    def connect(self, args):
        print "connect:", args
        self._db = MySQLdb.connect(**args)


    ## closes database connection
    # \brief It closes connection to the open database
    def close(self):
        if self._db:
            self._db.close()
#        pass

    ## fetches the required components
    # \param names list of component names
    # \returns list of given components
    def components(self, names): 
        argout = []
        if self._db is not None:
            try:
                cursor = self._db.cursor()
                for ar in names:
                    cursor.execute("select xml from components where name = '%s';" % ar.replace("'","\\\'"))
                    data=cursor.fetchone()
                    if not data or not data[0]:
                        raise NonregisteredDBRecordError, "Component %s not registered in the database" % ar
                    argout.append(data[0])
                cursor.close()    
            except:
                cursor.close()    
                raise
        print "components"
        return argout


    ## fetches the required datasources
    # \param names list of datasource names
    # \returns list of given datasources
    def dataSources(self, names):
        argout = []
        if self._db is not None:
            try:
                cursor = self._db.cursor()
                for ar in names:
                    cursor.execute("select xml from datasources where name = '%s';" % ar.replace("'","\\\'"))
                    data=cursor.fetchone()
                    if not data or not data[0]:
                        raise NonregisteredDBRecordError, "DataSource %s not registered in the database" % ar
                    argout.append(data[0])
                cursor.close()    
            except:
                cursor.close()    
                raise
#        print "dataSources"
        return argout



    ## fetches the names of available components
    # \returns list of available components
    def availableComponents(self):
        argout = []
        if self._db is not None:
            try:
                cursor = self._db.cursor()
                cursor.execute("select name from components;")
                data=cursor.fetchall()
                argout = [d[0] for d in data]
                cursor.close()    
            except:
                cursor.close()    
                raise

#        print "available components"
        return argout



    ## fetches the names of available datasources
    # \returns list of available datasources
    def availableDataSources(self):
        argout = []
        if self._db is not None:
            try:
                cursor = self._db.cursor()
                cursor.execute("select name from datasources;")
                data=cursor.fetchall()
                argout = [d[0] for d in data]
                cursor.close()    
            except:
                cursor.close()    
                raise
#        print "available datasources"
        return argout


    ## stores the given component
    # \param name name of the component to store
    # \param xml component tree
    def storeComponent(self, name, xml):
        if self._db is not None:
            try:
                cursor = self._db.cursor()
                cursor.execute("select exists(select 1 from components where name = '%s');" % name.replace("'","\\\'"))
                data=cursor.fetchone()
                if data[0]:
                    cursor.execute("update components set xml = '%s' where name = '%s';" 
                                   % (xml.replace("'","\\\'"), name.replace("'","\\\'")))
                else:
                    cursor.execute("insert into components values('%s', '%s', 0);" 
                                   % (name.replace("'","\\\'"), xml.replace("'","\\\'")))
                    
                self._db.commit()
                cursor.close()    
            except:
                self._db.rollback()
                cursor.close()    
                raise
    

            print "store component", name


    ## stores the given datasource
    # \param name name of the datasource to store
    # \param xml datasource tree
    def storeDataSource(self, name, xml):
        if self._db is not None:
            try:
                cursor = self._db.cursor()
                cursor.execute("select exists(select 1 from datasources where name = '%s');" % name.replace("'","\\\'"))
                data=cursor.fetchone()
                if data[0]:
                    cursor.execute("update datasources set xml = '%s' where name = '%s';" 
                                   % (xml.replace("'","\\\'"), name.replace("'","\\\'")))
                else:
                    cursor.execute("insert into datasources values('%s', '%s');" 
                                   % (name.replace("'","\\\'"), xml.replace("'","\\\'")))
                    
                self._db.commit()
                cursor.close()    
            except:
                self._db.rollback()
                cursor.close()    
                raise
            print "store DataSource", name


    ## deletes the given component
    # \param name of the component to delete
    def deleteComponent(self, name):
        if self._db is not None:
            try:
                cursor = self._db.cursor()
                cursor.execute("select exists(select 1 from components where name = '%s');" % name.replace("'","\\\'"))
                data=cursor.fetchone()
                if data[0]:
                    cursor.execute("delete from components where name = '%s';" % name.replace("'","\\\'"))
                    
                    self._db.commit()
                cursor.close()    
            except:
                self._db.rollback()
                cursor.close()    
                raise
    

            print "delete component", name



    ## sets components as mandatory
    # \param name of the component 
    def setMandatory(self, name):
        if self._db is not None:
            try:
                cursor = self._db.cursor()
                cursor.execute("select exists(select 1 from components where name = '%s');" % name.replace("'","\\\'"))
                data=cursor.fetchone()
                if data[0]:
                    cursor.execute("update components set mandatory = 1 where name = '%s';" %  name.replace("'","\\\'"))
                    
                    self._db.commit()
                cursor.close()    
            except:
                self._db.rollback()
                cursor.close()    
                raise
    

            print "unset mandatory", name

    ## sets components as not mandatory
    # \param name of the component to delete
    def unsetMandatory(self, name):
        if self._db is not None:
            try:
                cursor = self._db.cursor()
                cursor.execute("select exists(select 1 from components where name = '%s');" % name.replace("'","\\\'"))
                data=cursor.fetchone()
                if data[0]:
                    cursor.execute("update components set mandatory = 0 where name = '%s';" %  name.replace("'","\\\'"))
                    
                    self._db.commit()
                cursor.close()    
            except:
                self._db.rollback()
                cursor.close()    
                raise
    

            print "unset mandatory", name



    ## provides mandatory components
    # \returns list of mandatory components
    def mandatory(self):
        argout = []
        if self._db is not None:
            try:
                cursor = self._db.cursor()
                cursor.execute("select name from components where mandatory = 1")
                data=cursor.fetchall()
                argout = [d[0] for d in data]
                cursor.close()    
            except:
                raise
    

        print "mandatory"
        return argout   
            
    ## deletes the given datasource 
    # \param name of the datasource to delete
    def deleteDataSource(self, name):
        if self._db is not None:
            try:
                cursor = self._db.cursor()
                cursor.execute("select exists(select 1 from datasources where name = '%s');" % name.replace("'","\\\'"))
                data=cursor.fetchone()
                if data[0]:
                    cursor.execute("delete from datasources where name = '%s';" % name.replace("'","\\\'"))
                    
                    self._db.commit()
                cursor.close()    
            except:
                self._db.rollback()
                cursor.close()    
                raise
            print "delete DataSource", name


if __name__ == "__main__":

    import time

            
                
    
