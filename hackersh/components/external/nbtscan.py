# Copyright (C) 2013 Itzik Kotler
#
# This file is part of Hackersh.
#
# Hackersh is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# Hackersh is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hackersh; see the file COPYING.  If not,
# see <http://www.gnu.org/licenses/>.

import csv


# Local imports

import hackersh.objects


# Metadata

__author__ = "Itzik Kotler <xorninja@gmail.com>"
__version__ = "0.1.1"


# Implementation

class NbtScan(hackersh.objects.ExternalComponentStdoutOutput):

    class NbtScanStdoutOutputHandler(hackersh.objects.StdoutOutputHandler):

        def startDocument(self):

            self._names = {}

        def feed(self, data):

            for row in csv.reader(data.split('\n'), delimiter=','):

                # i.e. 192.168.1.106,TV             ,Workstation Service

                try:

                    (ip_addr, group_name, netbios_service) = row[:3]

                    self._names[group_name.strip().upper()] = self._names.get(group_name.strip().upper(), []) + [netbios_service.strip()]

                except Exception:

                    pass

        def endDocument(self):

            if self._names:

                self._output.append({'PROTO': 'UDP', 'PORT': '137', 'SERVICE': 'NETBIOS-NS', 'NETBIOS-NS': {'NAMES': self._names}})

    # Consts

    DEFAULT_FILENAME = "nbtscan"

    DEFAULT_OUTPUT_OPTIONS = "-v -h -q -s ,"

    DEFAULT_FILTER = DEFAULT_QUERY = "IPV4_ADDRESS"
