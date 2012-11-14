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
## \package ndtsconfigserver nexdatas
## \file ComponentParser.py
# Class for searching database names in components


from xml import sax

import sys, os



## SAX2 parser 
class ComponentHandler(sax.ContentHandler):

    ## constructor
    # \brief It constructs parser and defines the H5 output file
    # \param fileElement file element
    # \param decoders decoder pool
    def __init__(self):
        sax.ContentHandler.__init__(self)
        self.datasources = {}
        self.counter = 0 


    ##  parses the opening tag
    # \param name tag name
    # \param attrs attribute dictionary
    def startElement(self, name, attrs):
        if name == "datasource":
            if "name" in attrs.keys():
                aName = attrs["name"]
            else:
                aName = "__unnamed__%s" % self.counter
                self.counter += 1
            if "type" in attrs.keys():
                aType = attrs["type"]
            else:
                aType = ""
            self.datasources[aName] = aType    
            
            




if __name__ == "__main__":

    if  len(sys.argv) <2:
        print "usage: ComponentParser.py  <XMLinput>"
        
    else:
        ## input XML file
        fi = sys.argv[1]
        if os.path.exists(fi):

            ## a parser object
            parser = sax.make_parser()
            
            ## a SAX2 handler object
            handler = ComponentHandler()
            parser.setContentHandler(handler)
            parser.parse(open(fi))
            print handler.datasources


            ## a SAX2 handler object
            handler = ComponentHandler()
            sax.parseString("<datasource name ='myds' type = 'CLIENT'/> ", handler)
            print handler.datasources
    


if __name__ == "__main__":
    import sys

