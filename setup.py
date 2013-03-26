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
## \file setup.py
# ndts installer 
import os,sys
from distutils.core import setup
from distutils.command.install import install

## package name
NDTS = "mcs"
## ndts imported package
INDTS = __import__(NDTS)


#__requires__ = 'nextdata ==%s' % INDTS.__version__

## reading a file
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

## required files
required = [
    'numpy (>=1.5.0)',
    'PyTango (>=7.2.2)',
    'pninx (>=4.0.2)'
#    'libpninx (>=0.1.2)'
#   'pninx-python (>=0.1.2)'
#   'libpninx-python (>=0.1.2)'
#   'libpninx-python (>=0.1.2)'
    ]

## metadata for distutils
SETUPDATA=dict(
    name = "nexdatas.configserver",
    version = INDTS.__version__,
    author = "Jan Kotanski, Eugen Wintersberger , Halil Pasic",
    author_email = "jankotan@gmail.com, eugen.wintersberger@gmail.com, halil.pasic@gmail.com",
    description = ("Nexus Data writer implemented as a Tango Server"),
    license = "GNU GENERAL PUBLIC LICENSE v3",
    keywords = "configuration MySQL writer Tango server nexus data",
    url = "http://code.google.com/p/nexdatas/",
    packages=['mcs'],
    requires=required,
    scripts = ['XMLConfigServer.py', 'XMLConfigServer'],
#    scripts = ['TangoDataServer.py'],
#    package_data={'ndts': ['TDS']},
    long_description= read('README')
)

## metadata for setuptools
#SETUPTOOLSDATA= dict(
#    include_package_data = True,
#    install_requires = [
#        'numpy>=1.5.0',
#        'PyTango>=7.2.2',
#        'libpninx-python>=0.1.2'
#        ],
#)


        

## the main function
def main():
    setup(**SETUPDATA)
        

if __name__ == '__main__':
    main()

