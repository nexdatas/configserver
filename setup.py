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
#

""" setup.py for NXS configuration server """

import os
from distutils.core import setup, Command
from sphinx.setup_command import BuildDoc


#: package name
NXS = "nxsconfigserver"
#: nxs imported package
INXS = __import__(NXS)

# __requires__ = 'nextdata ==%s' % INXS.__version__


def read(fname):
    """ read the file

    :param fname: readme file name
    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


class TestCommand(Command):

    """ test command class
    """

    #: user options
    user_options = []

    #: initializes options
    def initialize_options(self):
        pass

    #: finalizes options
    def finalize_options(self):
        pass

    #: runs command
    def run(self):
        import sys
        import subprocess
        errno = subprocess.call([sys.executable, 'test/runtest.py'])
        raise SystemExit(errno)


release = INXS.__version__
version = ".".join(release.split(".")[:2])
name = "NXSConfigServer"


#: required files
REQUIRED = [
    'numpy (>=1.5.0)',
    'PyTango (>=7.2.2)',
    #    'libpninx (>=0.1.2)'
    #   'pninx-python (>=0.1.2)'
    #   'libpninx-python (>=0.1.2)'
    #   'libpninx-python (>=0.1.2)'
]


#: metadata for distutils
SETUPDATA = dict(
    name="nexdatas.configserver",
    version=INXS.__version__,
    author="Jan Kotanski, Eugen Wintersberger , Halil Pasic",
    author_email="jankotan@gmail.com, eugen.wintersberger@gmail.com, "
    "halil.pasic@gmail.com",
    description=("Configuration Server for Nexus Data Writer"),
    license="GNU GENERAL PUBLIC LICENSE v3",
    keywords="configuration MySQL writer Tango server nexus data",
    url="http://github.com/jkotan/nexdatas/",
    packages=[NXS],
    requires=REQUIRED,
    scripts=['NXSConfigServer'],
    cmdclass={'test': TestCommand, 'build_sphinx': BuildDoc},
    command_options={
        'build_sphinx': {
            'project': ('setup.py', name),
            'version': ('setup.py', version),
            'release': ('setup.py', release)}},
    long_description=read('README.rst')
)


def main():
    """ the main function """
    setup(**SETUPDATA)


if __name__ == '__main__':
    main()
