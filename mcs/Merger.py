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
## \package ndtsconfigserver nexdatas
## \file Merger.py
# Class for merging DOM component trees

from xml.dom.minidom import Document, parseString, Element
from Errors import IncompatibleNodeError, UndefinedTagError

## merges the components
class Merger(object):
    
    ## constructor
    def __init__(self):
        
        ## DOM root node
        self.__root = None
        ## tags which cannot have the same siblings
        self.singles =['datasource', 'strategy', 'dimensions', 'definition',
                       'record', 'device', 'query', 'database', 'door']

        ## allowed children
        self.children ={
            "datasource":("record", "doc", "device", "database", "query", "door"),
            "attribute":("datasource", "strategy", "enumeration", "doc"),
            "definition":("group", "field", "attribute", "link", "component", "doc", "symbols"),
            "dimensions":("dim", "doc"),
            "field":("attribute", "datasource", "doc", "dimensions", "enumeration", "strategy"),
            "group":("group", "field", "attribute", "link", "component", "doc"),
            "link":("doc")
            }

        ## with unique text
        self.uniqueText = ['field']

    ## collects text from text child nodes
    # \param node parent node    
    def __getText(self, node):
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
        attr = node.attributes

        name = node.getAttribute("name") if isinstance(node, Element) else "" 

        if node and node.parentNode and node.parentNode.nodeName != '#document':
#            print node.nodeName()
            res =  self.__getAncestors(node.parentNode) 
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
        attr1 = elem1.attributes
        attr2 = elem2.attributes
        status = True
        tags = []
 
        name1 = elem1.getAttribute("name")
        name2 = elem2.getAttribute("name")

        if name1 != name2 :
            if tagName in self.singles:
                raise IncompatibleNodeError("Incompatible element attributes  %s: " % str(tags), [elem1, elem2])
                
            return False

        for i1 in range(attr1.length):
            for i2 in range(attr2.length):
                at1 = attr1.item(i1)
                at2 = attr2.item(i2)
                if at1.nodeName == at2.nodeName and at1.nodeValue != at2.nodeValue:
                    status = False
                    tags.append((str(self.__getAncestors(at1)),
                                 str(at1.nodeValue) , str(at2.nodeValue)))

        if not status  and ( tagName in self.singles  or name1 ): 
            raise IncompatibleNodeError("Incompatible element attributes  %s: " % str(tags), [elem1, elem2])
                


        if tagName in self.uniqueText:
            text1=unicode(self.__getText(elem1)).strip()
            text2=unicode(self.__getText(elem2)).strip()         
            ## TODO white spaces?
            if text1 != text2 and text1 and text2:
                raise IncompatibleNodeError(
                    "Incompatible \n%s element value\n%s \n%s "  \
                        % (str(self.__getAncestors(elem1)), text1, text2),
                    [elem1, elem2])
                    
            
        return status

    ## merges two dom elements 
    # \param elem1 first element
    # \param elem2 second element
    def __mergeNodes(self,elem1, elem2):
        tagName = elem1.nodeName
        attr1 = elem1.attributes
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
        while child2 : 
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
        status = False
        if node:
#            print "merging the children of: ", node.nodeName()
            changes = True
            
            while changes:
                children = node.childNodes
                changes = False
                for c1 in range(children.length):
                    child1 = children.item(c1)
                    for c2 in range(children.length):
                        child2 = children.item(c2)
                        if child1 != child2:
                            if isinstance(child1, Element) and isinstance(child2, Element):
                                #                            if elem1 is not None and elem2 is not None:
                                if self.__areMergeable(child1, child2):
                                    self.__mergeNodes(child1, child2)
                                    changes = True
                                    status = True
                        if changes:
                            break
                    if changes:
                        break
                        
            child = node.firstChild
            nName = unicode(node.nodeName) if isinstance(node, Element) else ""

            while child:
                if nName and nName in self.children.keys():
                    cName = unicode(child.nodeName) if isinstance(child, Element)  else ""
                    if cName and cName not in self.children[nName]:
                        raise IncompatibleNodeError(
                            "Not allowed <%s> child of \n < %s > \n  parent"  \
                                % (cName, self.__getAncestors(child)),
                            [child])
                                
                self.__mergeChildren(child)
                child = child.nextSibling


                
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
                    raise  UndefinedTagError, "<definition> not defined"
                rootDef = rdef[0]
            else:
                defin = dcp.getElementsByTagName("definition")
                if not defin: 
                    raise  UndefinedTagError, "<definition> not defined"
                for cd in defin[0].childNodes:
                    icd = self.__root.importNode(cd, True) 
                    rootDef.appendChild(icd)

    ## Converts DOM trer to string
    #  \returns DOM tree in XML string
    def toString(self):
        if self.__root:
#            return self.__root.toxml()
#            xml = self.__root.toxml()
#            reparsed = parseString(xml)
#            return reparsed.toprettyxml(indent=" ",newl="")
            
            return str((self.__root.toprettyxml(indent=" ",newl=""))).replace("\n \n "," ").replace("\n\n","\n")
#            return self.__root.toprettyxml(indent=" ",newl="")

    ## performs the merging operation
    # \brief It calls mergeChildern() method
    def merge(self):
        self.__mergeChildren(self.__root)

if __name__ == "__main__":
    import sys

