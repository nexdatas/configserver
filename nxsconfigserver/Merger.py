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
## \package nxsconfigserver nexdatas
## \file Merger.py
# Class for merging DOM component trees

""" Classes for merging DOM component trees """

import re

from xml.dom.minidom import parseString, Element
from .Errors import IncompatibleNodeError, UndefinedTagError


## merges the components
class Merger(object):

    ## constructor
    def __init__(self):

        ## DOM root node
        self.__root = None
        ## tags which cannot have the same siblings
        self.singles = ['strategy', 'dimensions', 'definition',
                        'record', 'device', 'query', 'database']

        ## allowed children
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
            "link": ("doc"),
            "dim": ("datasource", "strategy", "doc"),
            }

        ## with unique text
        self.uniqueText = ['field', 'attribute', 'query', 'strategy', 'result']

        ## node which can have switched strategy
        self.switchable = ["field", 'attribute']

        ## strategy modes to switch
        self.modesToSwitch = ["INIT", "FINAL"]

        ## aliased to switch to STEP mode
        self.stepdatasources = []

        self.__dsvars = "$datasources."

    ## collects text from text child nodes
    # \param node parent node
    @classmethod
    def __getText(cls, node):
        text = ""
        if node:
            child = node.firstChild
            while child:
                if child.nodeType == child.TEXT_NODE:
                    text += child.data
                child = child.nextSibling
        return text

    ## gets ancestors form the xml tree
    # \param node dom node
    # \returns xml path
    def __getAncestors(self, node):
        res = ""

        name = node.getAttribute("name") if isinstance(node, Element) else ""

        if node and node.parentNode and \
                node.parentNode.nodeName != '#document':
            res = self.__getAncestors(node.parentNode)
        res += "/" + unicode(node.nodeName)
        if name:
            res += ":" + name
        return res

    ## checks if two elements are mergeable
    # \param elem1 first element
    # \param elem2 second element
    # \returns bool varaible if two elements are mergeable
    def __areMergeable(self, elem1, elem2):
#        return False
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
            if (tagName in self.singles
                or (name1 and name1 == name2)):
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

    ## checks if two elements are mergeable
    # \param elem1 first element
    # \param elem2 second element
    # \returns tags with not mergeable attributes
    def __checkAttributes(self, elem1, elem2):
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

    ## merges two dom elements
    # \param elem1 first element
    # \param elem2 second element
    @classmethod
    def __mergeNodes(cls, elem1, elem2):
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

    ## merge the given node
    # \param node the given node
    def __mergeChildren(self, node):
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

    ## find first datasources node and name in text nodes of the node
    # \params node the parent node
    # \returns (node, name) of the searched datasource
    def __getTextDataSource(self, node):            
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
            if name in self.stepdatasources:
                dsnode = node
                dsname = name
                break 
            text =  text[(index + len(name) + len(self.__dsvars) + 2):]
            index = text.find(self.__dsvars)
        return dsname, dsnode    

    ## switch the given node to step mode
    # \param node the given node
    def __switch(self, node):
        if node:
            stnode = None
            mode = None
            dsname = None
            dsnode = None

            dsname, dsnode = self.__getTextDataSource(node)
                        
            children = node.childNodes
            cpname = node.getAttribute("name")
            for child in children:
                cName = unicode(child.nodeName) \
                    if isinstance(child, Element) else ""
                if cName == 'datasource':
                    dsname = child.getAttribute("name")
                    if dsname in self.stepdatasources:
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
                                if gdsname in self.stepdatasources:
                                    dsnode = child
#                        if not dsnode:            
#                            break
                elif cName == 'strategy':
                    mode = child.getAttribute("mode")
                    if mode in self.modesToSwitch:
                        stnode = child
                    else:
                        break
                if stnode and dsnode:
                    break
            if stnode and dsnode:
                stnode.setAttribute("mode", "STEP")

    ## collects the given components in one DOM tree
    # \param components given components
    def collect(self, components):
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

    ## Converts DOM trer to string
    #  \returns DOM tree in XML string
    def toString(self):
        if self.__root:
            return str(self.__root.toxml())

    ## performs the merging operation
    # \brief It calls mergeChildern() method
    def merge(self):
        self.__mergeChildren(self.__root)


if __name__ == "__main__":
    pass
