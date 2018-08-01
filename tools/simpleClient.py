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
# \package tools tools for configserver
# \file simpleClient.py
# first example of simple client

import PyTango


# the main function
def main():
    device = "p09/mcs/r228"

    dpx = PyTango.DeviceProxy(device)
    dpx.set_timeout_millis(25000)
    dpx.Init()
    dpx.JSONSettings = '{"db": "ndts",  "host":"localhost" ,' \
                       + '"read_default_file":"/etc/my.cnf" }'


if __name__ == "__main__":
    main()
