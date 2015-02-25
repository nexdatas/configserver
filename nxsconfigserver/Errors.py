#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2015 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
## \package nxsconfigserver nexdatas
## \file Errors.py
# Error classes

""" Error classes  """


## Incompatible class Exception
class IncompatibleNodeError(Exception):

    ## constructor
    # \param value string with error message
    # \param nodes list of nodes with errors
    def __init__(self, value, nodes=None):
        Exception.__init__(self, value)
        ## exception value
        self.value = value
        ## nodes with errors
        self.nodes = nodes if nodes else []

    ## tostring method
    # \brief It shows the error message
    def __str__(self):
        return repr(self.value)


## Exception for undefined tags
class UndefinedTagError(Exception):
    pass


##  Error for non-existing database records
class NonregisteredDBRecordError(Exception):
    pass
