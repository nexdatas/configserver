#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2017 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
#

""" Error classes  """


class IncompatibleNodeError(Exception):

    """ Incompatible class Exception
    """

    def __init__(self, value, nodes=None):
        """ constructor

        :param value: string with error message
        :type value: :obj:`str`
        :param nodes: list of nodes with errors
        :type nodes: :obj:`list` <:class:`lxml.etree.Element`>
        """
        Exception.__init__(self, value)
        #: exception value
        self.value = value
        #: nodes with errors
        self.nodes = nodes if nodes else []

    def __str__(self):
        """ tostring method

        :brief: It shows the error message
        :rtype: :obj:`str`
        :returns: error message
        """
        return repr(self.value)


class UndefinedTagError(Exception):

    """ Exception for undefined tags
    """
    pass


class WrongXMLError(Exception):

    """ Exception for undefined tags
    """
    pass


class WrongJSONError(Exception):

    """ Exception for undefined tags
    """
    pass


class NonregisteredDBRecordError(Exception):

    """ Error for non-existing database records
    """
    pass
