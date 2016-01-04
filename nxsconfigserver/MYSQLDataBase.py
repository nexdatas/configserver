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
## \package mcs nexdatas.configserver
## \file MYSQLDataBase.py
# Allows the access to MYSQL database with NDTS configuration files
#

""" Providesthe access to MYSQL database with NDTS configuration files """

import MySQLdb

from .Errors import NonregisteredDBRecordError
from . import Streams


## XML Configurer
class MYSQLDataBase(object):
    ## constructor
    # \brief It creates the MYSQLDataBase instance
    def __init__(self):
        ## db instance
        self.__db = None
        self.__args = None

    ## connects to the database
    # \param args arguments of the MySQLdb connect method
    def connect(self, args):
        Streams.info("MYSQLDataBase::connect() - connect: %s" % args)
        self.__db = MySQLdb.connect(**args)
        self.__args = args

    ## closes database connection
    # \brief It closes connection to the open database
    def close(self):
        if self.__db:
            try:
                self.__db.ping(True)
                if self.__db.open:
                    self.__db.close()
            except:
                pass

    ## provides DB configuration version
    # \returns DB configuration version
    def version(self):
        argout = None
        if self.__db is not None:
            try:
                self.__db.ping(True)
                if not self.__db.open:
                    self.connect(self.__args)
                cursor = self.__db.cursor()
                cursor.execute(
                    "select value from properties where name = 'revision';")
                data = cursor.fetchone()
                if not data or not data[0]:
                    raise NonregisteredDBRecordError(
                        "Component %s not registered in the database"
                        % self.__args)
                argout = data[0]
                cursor.close()
            except:
                cursor.close()
                raise
        return argout

    ## adds escape characters to string
    # \param string
    # \retruns string with excape characters
    @classmethod
    def __escape(cls, string):
        return string.replace("\\", "\\\\").replace("'", "\\\'")

    ## increases revision number
    # \param cursor transaction cursor
    @classmethod
    def __incRevision(cls, cursor):
        cursor.execute(
            "select value from properties where name = 'revision';")
        data = cursor.fetchone()
        new = str(long(data[0]) + 1)
        cursor.execute(
            "update properties set value = '%s' where name = 'revision';"
            % (cls.__escape(new)))

    ## fetches the required components
    # \param names list of component names
    # \returns list of given components
    def components(self, names):
        argout = []
        if self.__db is not None:
            try:
                self.__db.ping(True)
                if not self.__db.open:
                    self.connect(self.__args)
                cursor = self.__db.cursor()
                for ar in names:
                    cursor.execute(
                        "select xml from components where name = '%s';"
                        % self.__escape(ar))
                    data = cursor.fetchone()
                    if not data or not data[0]:
                        raise NonregisteredDBRecordError(
                            "Component %s not registered in the database" % ar)
                    argout.append(data[0])
                cursor.close()
            except:
                cursor.close()
                raise
        return argout

    ## fetches the required selections
    # \param names list of selection names
    # \returns list of given selections
    def selections(self, names):
        argout = []
        if self.__db is not None:
            try:
                self.__db.ping(True)
                if not self.__db.open:
                    self.connect(self.__args)
                cursor = self.__db.cursor()
                for ar in names:
                    cursor.execute(
                        "select selection from selections where name = '%s';"
                        % self.__escape(ar))
                    data = cursor.fetchone()
                    if not data or not data[0]:
                        raise NonregisteredDBRecordError(
                            "Selection %s not registered in the database" % ar)
                    argout.append(data[0])
                cursor.close()
            except:
                cursor.close()
                raise
        return argout

    ## fetches the required datasources
    # \param names list of datasource names
    # \returns list of given datasources
    def dataSources(self, names):
        argout = []
        if self.__db is not None:
            try:
                self.__db.ping(True)
                if not self.__db.open:
                    self.connect(self.__args)
                cursor = self.__db.cursor()
                for ar in names:
                    cursor.execute(
                        "select xml from datasources where name = '%s';"
                        % self.__escape(ar))
                    data = cursor.fetchone()
                    if not data or not data[0]:
                        raise NonregisteredDBRecordError(
                            "DataSource %s not registered in the database"
                            % ar)
                    argout.append(data[0])
                cursor.close()
            except:
                cursor.close()
                raise
        return argout

    ## fetches the names of available components
    # \returns list of available components
    def availableComponents(self):
        argout = []
        if self.__db is not None:
            try:
                self.__db.ping(True)
                cursor = self.__db.cursor()
                cursor.execute("select name from components;")
                data = cursor.fetchall()
                argout = [d[0] for d in data]
                cursor.close()
            except:
                cursor.close()
                raise

        return argout

    ## fetches the names of available selections
    # \returns list of available selections
    def availableSelections(self):
        argout = []
        if self.__db is not None:
            try:
                self.__db.ping(True)
                cursor = self.__db.cursor()
                cursor.execute("select name from selections;")
                data = cursor.fetchall()
                argout = [d[0] for d in data]
                cursor.close()
            except:
                cursor.close()
                raise

        return argout

    ## fetches the names of available datasources
    # \returns list of available datasources
    def availableDataSources(self):
        argout = []
        if self.__db is not None:
            try:
                self.__db.ping(True)
                if not self.__db.open:
                    self.connect(self.__args)
                cursor = self.__db.cursor()
                cursor.execute("select name from datasources;")
                data = cursor.fetchall()
                argout = [d[0] for d in data]
                cursor.close()
            except:
                cursor.close()
                raise
        return argout

    ## stores the given component
    # \param name name of the component to store
    # \param xml component tree
    def storeComponent(self, name, xml):
        if self.__db is not None:
            try:
                self.__db.ping(True)
                if not self.__db.open:
                    self.connect(self.__args)
                cursor = self.__db.cursor()
                cursor.execute(
                    "select xml from components where name = '%s';"
                    % self.__escape(name))
                data = cursor.fetchone()
                if data and len(data) > 0 and data[0]:
                    if data[0] != xml:
                        cursor.execute(
                            "update components set xml"
                            " = '%s' where name = '%s';"
                            % (self.__escape(xml),
                               self.__escape(name)))
                        self.__incRevision(cursor)
                        self.__db.commit()
                    else:
                        self.__db.rollback()
                else:
                    cursor.execute(
                        "insert into components "
                        "values('%s', '%s', 0);"
                        % (self.__escape(name),
                           self.__escape(xml)))
                    self.__incRevision(cursor)
                    self.__db.commit()
                cursor.close()
            except:
                self.__db.rollback()
                cursor.close()
                raise

            Streams.info("MYSQLDataBase::storeComponent()"
                         " - store component %s" % name)

    ## stores the given datasource
    # \param name name of the datasource to store
    # \param xml datasource tree
    def storeDataSource(self, name, xml):
        if self.__db is not None:
            try:
                self.__db.ping(True)
                if not self.__db.open:
                    self.connect(self.__args)
                cursor = self.__db.cursor()
                cursor.execute(
                    "select xml from datasources where name = '%s';"
                    % self.__escape(name))
                data = cursor.fetchone()
                if data and len(data) > 0 and data[0]:
                    if data[0] != xml:
                        cursor.execute(
                            "update datasources set "
                            "xml = '%s' where name = '%s';"
                            % (self.__escape(xml),
                               self.__escape(name)))
                        self.__incRevision(cursor)
                        self.__db.commit()
                    else:
                        self.__db.rollback()
                else:
                    cursor.execute(
                        "insert into datasources "
                        "values('%s', '%s');"
                        % (self.__escape(name),
                           self.__escape(xml)))

                    self.__incRevision(cursor)
                    self.__db.commit()
                cursor.close()
            except:
                self.__db.rollback()
                cursor.close()
                raise
            Streams.info("MYSQLDataBase::storeDataSource() "
                         "- store datasource %s" % name)

    ## stores the given selection
    # \param name name of the selection to store
    # \param selection selection tree
    def storeSelection(self, name, selection):
        if self.__db is not None:
            try:
                self.__db.ping(True)
                if not self.__db.open:
                    self.connect(self.__args)
                cursor = self.__db.cursor()
                cursor.execute(
                    "select selection from selections where name = '%s';"
                    % self.__escape(name))
                data = cursor.fetchone()
                if data and len(data) > 0 and data[0]:
                    if data[0] != selection:
                        cursor.execute(
                            "update selections set "
                            "selection = '%s' where name = '%s';"
                            % (self.__escape(selection),
                               self.__escape(name)))
#                        self.__incRevision(cursor)
                        self.__db.commit()
                    else:
                        self.__db.rollback()
                else:
                    cursor.execute(
                        "insert into selections "
                        "values('%s', '%s');"
                        % (self.__escape(name),
                           self.__escape(selection)))

#                    self.__incRevision(cursor)
                    self.__db.commit()
                cursor.close()
            except:
                self.__db.rollback()
                cursor.close()
                raise
            Streams.info("MYSQLDataBase::storeSelection() "
                         "- store selection %s" % name)

    ## deletes the given component
    # \param name of the component to delete
    def deleteComponent(self, name):
        if self.__db is not None:
            try:
                self.__db.ping(True)
                if not self.__db.open:
                    self.connect(self.__args)
                cursor = self.__db.cursor()
                cursor.execute(
                    "select exists(select 1 from components where "
                    "name = '%s');" % self.__escape(name))
                data = cursor.fetchone()
                if data[0]:
                    cursor.execute(
                        "delete from components where name = '%s';"
                        % self.__escape(name))

                    self.__db.commit()
                self.__incRevision(cursor)
                cursor.close()
            except:
                self.__db.rollback()
                cursor.close()
                raise

            Streams.info("MYSQLDataBase::deleteComponent() "
                         "- delete component %s" % name)

    ## deletes the given selection
    # \param name of the selection to delete
    def deleteSelection(self, name):
        if self.__db is not None:
            try:
                self.__db.ping(True)
                if not self.__db.open:
                    self.connect(self.__args)
                cursor = self.__db.cursor()
                cursor.execute(
                    "select exists(select 1 from selections where "
                    "name = '%s');" % self.__escape(name))
                data = cursor.fetchone()
                if data[0]:
                    cursor.execute(
                        "delete from selections where name = '%s';"
                        % self.__escape(name))

                    self.__db.commit()
#                self.__incRevision(cursor)
                cursor.close()
            except:
                self.__db.rollback()
                cursor.close()
                raise

            Streams.info("MYSQLDataBase::deleteSelection() "
                         "- delete selection %s" % name)

    ## sets components as mandatory
    # \param name of the component
    def setMandatory(self, name):
        if self.__db is not None:
            try:
                self.__db.ping(True)
                if not self.__db.open:
                    self.connect(self.__args)
                cursor = self.__db.cursor()
                cursor.execute(
                    "select mandatory from components where name = '%s';"
                    % self.__escape(name))
                data = cursor.fetchone()
                if data and len(data) > 0 and data[0] != 1:
                    cursor.execute(
                        "update components set mandatory = 1 where "
                        "name = '%s';" % self.__escape(name))
                    self.__db.commit()
                    self.__incRevision(cursor)
                else:
                    self.__db.rollback()
                cursor.close()
            except:
                self.__db.rollback()
                cursor.close()
                raise
            Streams.info(
                "MYSQLDataBase::setMandatory() - component %s" % name)

    ## sets components as not mandatory
    # \param name of the component to delete
    def unsetMandatory(self, name):
        if self.__db is not None:
            try:
                self.__db.ping(True)
                if not self.__db.open:
                    self.connect(self.__args)
                cursor = self.__db.cursor()
                cursor.execute(
                    "select mandatory from components where name = '%s';"
                    % self.__escape(name))
                data = cursor.fetchone()
                if data and len(data) > 0 and data[0] != 0:
                    cursor.execute(
                        "update components set mandatory = 0 where "
                        "name = '%s';" % self.__escape(name))

                    self.__db.commit()
                    self.__incRevision(cursor)
                else:
                    self.__db.rollback()

                cursor.close()
            except:
                self.__db.rollback()
                cursor.close()
                raise

            Streams.info("MYSQLDataBase::unsetMandatory() "
                         "- component %s" % name)

    ## provides mandatory components
    # \returns list of mandatory components
    def mandatory(self):
        argout = []
        if self.__db is not None:
            try:
                self.__db.ping(True)
                if not self.__db.open:
                    self.connect(self.__args)
                cursor = self.__db.cursor()
                cursor.execute(
                    "select name from components where mandatory = 1")
                data = cursor.fetchall()
                argout = [d[0] for d in data]
                cursor.close()
            except:
                raise

        return argout

    ## deletes the given datasource
    # \param name of the datasource to delete
    def deleteDataSource(self, name):
        if self.__db is not None:
            try:
                self.__db.ping(True)
                if not self.__db.open:
                    self.connect(self.__args)
                cursor = self.__db.cursor()
                cursor.execute(
                    "select exists(select 1 from datasources where "
                    "name = '%s');" % self.__escape(name))
                data = cursor.fetchone()
                if data[0]:
                    cursor.execute(
                        "delete from datasources where name = '%s';"
                        % self.__escape(name))

                    self.__db.commit()
                self.__incRevision(cursor)
                cursor.close()
            except:
                self.__db.rollback()
                cursor.close()
                raise
            Streams.info("MYSQLDataBase::deleteDataSource() "
                         "- datasource %s" % name)


if __name__ == "__main__":
    pass
