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
#

""" Classes for merging DOM component trees """

import re

from xml.dom.minidom import parseString, Element
from .Errors import IncompatibleNodeError, UndefinedTagError


class Merger(object):
    """ merges the components
    """

    def __init__(self):
        """ consturctor
        """

        #: (:obj:`xml.dom.minidom.Node`) DOM root node
        self.__root = None
        #: (:obj:`list` <:obj:`str`> ) tags which cannot have the same siblings
        self.singles = ['strategy', 'dimensions', 'definition',
                        'record', 'device', 'query', 'database']

        #: (:obj:`dict` <:obj:`str` , :obj:`tuple` <:obj:`str`>> ) \
        #:    allowed children
        self.children = {
            "attribute": ("datasource", "strategy", "enumeration",
                          "doc", "dimensions"),
            "definition": ("group", "field", "attribute", "link",
                           "component", "doc", "symbols"),
            "dimensions": ("dim", "doc"),
            "field": ("attribute", "datasource", "doc", "dimensions",
                      "enumeration", "strategy"),
            "group": ("group", "field", "attribute", "link", "component",
                      "doc"),
            "link": ("datasource", "strategy", "doc"),
            "dim": ("datasource", "strategy", "doc"),
        }

        #: (:obj:`list` <:obj:`str`> ) with unique text
        self.uniqueText = ['field', 'attribute', 'query', 'strategy', 'result']

        #: (:obj:`list` <:obj:`str`> ) node which can have switched strategy
        self.switchable = ["field", 'attribute']

        #: (:obj:`dict` <:obj:`str` , :obj:`str`> ) \
        #:     strategy modes to switch
        self.modesToSwitch = {
            "INIT": "STEP",
            "FINAL": "STEP"
        }

        #: (:obj:`list` <:obj:`str`> ) aliased to switch to STEP mode
        self.switchdatasources = []

        #: (:obj:`str`) datasource label
        self.__dsvars = "$datasources."

    @classmethod
    def __getText(cls, node):
        """ collects text from text child nodes

        :param node: parent node
        :type node: :obj:`xml.dom.minidom.Node`
        """
        text = ""
        if node:
            child = node.firstChild
            while child:
                if child.nodeType == child.TEXT_NODE:
                    text += child.data
                child = child.nextSibling
        return text

    def __getAncestors(self, node):
        """ gets ancestors form the xml tree

        :param node: dom node
        :type node: :obj:`xml.dom.minidom.Node`
        :returns: xml path
        :rtype: :obj:`str`
        """
        res = ""

        name = node.getAttribute("name") if isinstance(node, Element) else ""

        if node and node.parentNode and \
                node.parentNode.nodeName != '#document':
            res = self.__getAncestors(node.parentNode)
        res += "/" + unicode(node.nodeName)
        if name:
            res += ":" + name
        return res

    def __areMergeable(self, elem1, elem2):
        """ checks if two elements are mergeable

        :param elem1: first element
        :type elem1: :obj:`xml.dom.minidom.Element`
        :param elem2: second element
        :type elem2: :obj:`xml.dom.minidom.Element`
        :returns: bool varaible if two elements are mergeable
        :rtype: :obj:`bool`
        """

        if elem1.nodeName != elem2.nodeName:
            return False
        tagName = unicode(elem1.nodeName)
        status = True

        name1 = elem1.getAttribute("name")
        name2 = elem2.getAttribute("name")

        if name1 != name2 and name1 and name2:
            if tagName in self.singles:
                raise IncompatibleNodeError(
                    "Incompatible element attributes  %s: "
                    % str((str(self.__getAncestors(elem1)), str(name2))),
                    [elem1, elem2])
            return False

        tags = self.__checkAttributes(elem1, elem2)
        if tags:
            status = False
            if tagName in self.singles or (name1 and name1 == name2):
                raise IncompatibleNodeError(
                    "Incompatible element attributes  %s: "
                    % str(tags), [elem1, elem2])

        if tagName in self.uniqueText:
            text1 = unicode(self.__getText(elem1)).strip()
            text2 = unicode(self.__getText(elem2)).strip()
            if text1 != text2 and text1 and text2:
                raise IncompatibleNodeError(
                    "Incompatible \n%s element value\n%s \n%s "
                    % (str(self.__getAncestors(elem1)), text1, text2),
                    [elem1, elem2])

        return status

    def __checkAttributes(self, elem1, elem2):
        """ checks if two elements are mergeable

        :param elem1: first element
        :type elem1: :obj:`xml.dom.minidom.Element`
        :param elem2: second element
        :type elem2: :obj:`xml.dom.minidom.Element`
        :returns: tags with not mergeable attributes
        :rtype: :obj:`list` <:obj:`tuple` <:obj:`str`>>
        """
        tags = []
        attr1 = elem1.attributes
        attr2 = elem2.attributes
        for i1 in range(attr1.length):
            for i2 in range(attr2.length):
                at1 = attr1.item(i1)
                at2 = attr2.item(i2)
                if at1.nodeName == at2.nodeName \
                        and at1.nodeValue != at2.nodeValue:
                    tags.append((str(self.__getAncestors(at1)),
                                 str(at1.nodeValue), str(at2.nodeValue)))
        return tags

    @classmethod
    def __mergeNodes(cls, elem1, elem2):
        """ merges two dom elements

        :param elem1: first element
        :type elem1: :obj:`xml.dom.minidom.Element`
        :param elem2: second element
        :type elem2: :obj:`xml.dom.minidom.Element`
        """
        attr2 = elem2.attributes
        texts = []

        for i2 in range(attr2.length):
            at2 = attr2.item(i2)
            elem1.setAttribute(at2.nodeName, at2.nodeValue)

        child1 = elem1.firstChild
        while child1:
            if child1.nodeType == child1.TEXT_NODE:
                texts.append(unicode(child1.data).strip())
            child1 = child1.nextSibling

        toMove = []

        child2 = elem2.firstChild
        while child2:
            if child2.nodeType == child2.TEXT_NODE:
                if unicode(child2.data).strip() not in texts:
                    toMove.append(child2)
            else:
                toMove.append(child2)
            child2 = child2.nextSibling

        for child in toMove:
            elem1.appendChild(child)
        toMove = []

        parent = elem2.parentNode
        parent.removeChild(elem2)

    def __mergeChildren(self, node):
        """ merge the given node

        :param node: the given node
        :type node: :obj:`xml.dom.minidom.Node`
        """
        if node:

            children = node.childNodes
            c1 = 0
            while c1 < children.length:
                child1 = children.item(c1)
                c2 = c1 + 1
                while c2 < children.length:
                    child2 = children.item(c2)
                    if child1 != child2:
                        if isinstance(child1, Element) \
                                and isinstance(child2, Element):
                            if self.__areMergeable(child1, child2):
                                self.__mergeNodes(child1, child2)
                                c2 -= 1
                    c2 += 1
                c1 += 1

            child = node.firstChild
            nName = unicode(node.nodeName) if isinstance(node, Element) else ""

            while child:
                cName = unicode(child.nodeName) \
                    if isinstance(child, Element) else ""
                if nName and nName in self.children.keys():
                    if cName and cName not in self.children[nName]:
                        raise IncompatibleNodeError(
                            "Not allowed <%s> child of \n < %s > \n  parent"
                            % (cName, self.__getAncestors(child)),
                            [child])

                self.__mergeChildren(child)
                if cName in self.switchable:
                    self.__switch(child)
                child = child.nextSibling

    def __getTextDataSource(self, node):
        """ find first datasources node and name in text nodes of the node

        :param node: the parent node
        :type node: :obj:`xml.dom.minidom.Node`
        :returns: (node, name) of the searched datasource
        :rtype: (:obj:`str` , :obj:`str`)
        """
        dsname = None
        dsnode = None
        text = unicode(self.__getText(node)).strip()
        index = text.find(self.__dsvars)
        while index >= 0:
            try:
                subc = re.finditer(
                    r"[\w]+",
                    text[(index + len(self.__dsvars)):]).next().group(0)
            except:
                subc = ''
            name = subc.strip() if subc else ""
            if name in self.switchdatasources:
                dsnode = node
                dsname = name
                break
            text = text[(index + len(name) + len(self.__dsvars) + 2):]
            index = text.find(self.__dsvars)
        return dsname, dsnode

    def __switch(self, node):
        """ switch the given node to step mode

        :param node: the given node
        :type node: :obj:`xml.dom.minidom.Node`
        """
        if node:
            stnode = None
            mode = None
            dsname = None
            dsnode = None

            dsname, dsnode = self.__getTextDataSource(node)

            children = node.childNodes
            for child in children:
                cName = unicode(child.nodeName) \
                    if isinstance(child, Element) else ""
                if cName == 'datasource':
                    dsname = child.getAttribute("name")
                    if dsname in self.switchdatasources:
                        dsnode = child
                    else:
                        dsname, dsnode = self.__getTextDataSource(child)
                    if not dsnode:
                        gchildren = child.childNodes
                        for gchild in gchildren:
                            gcName = unicode(gchild.nodeName) \
                                if isinstance(gchild, Element) else ""
                            if gcName == 'datasource':
                                gdsname = gchild.getAttribute("name")
                                if gdsname in self.switchdatasources:
                                    dsnode = child
                elif cName == 'strategy':
                    mode = child.getAttribute("mode")
                    if mode in self.modesToSwitch.keys():
                        stnode = child
                    else:
                        break
                if stnode and dsnode:
                    break
            if stnode and dsnode:
                stnode.setAttribute("mode", self.modesToSwitch[mode])

    def collect(self, components):
        """ collects the given components in one DOM tree

        :param components: given components
        :type components: :obj:`list` <:obj:`str`>
        """
        self.__root = None
        rootDef = None
        for cp in components:
            dcp = None
            if cp:
                dcp = parseString(cp)
            if not dcp:
                continue

            if self.__root is None:
                self.__root = dcp
                rdef = dcp.getElementsByTagName("definition")
                if not rdef:
                    raise UndefinedTagError("<definition> not defined")
                rootDef = rdef[0]
            else:
                defin = dcp.getElementsByTagName("definition")
                if not defin:
                    raise UndefinedTagError("<definition> not defined")
                for cd in defin[0].childNodes:
                    if cd.nodeType != cd.TEXT_NODE or \
                            (cd.nodeType == cd.TEXT_NODE
                             and str(cd.data).strip()):

                        icd = self.__root.importNode(cd, True)
                        rootDef.appendChild(icd)

    def toString(self):
        """ Converts DOM tree to string

        :returns: DOM tree in XML string
        :rtype: :obj:`str`
        """
        if self.__root:
            return str(self.__root.toxml())

    def merge(self):
        """ performs the merging operation
        """
        self.__mergeChildren(self.__root)


if __name__ == "__main__":
    pass
