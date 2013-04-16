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
__version__ = "0.1.0"


# Implementation

class Nbtscan(hackersh.objects.ExternalComponentStdoutOutput):

    def _processor(self, context, data):

        names = {}

        for row in csv.reader(data.split('\n'), delimiter=','):

            # i.e. 192.168.1.106,TV             ,Workstation Service

            try:

                (ip_addr, group_name, netbios_service) = row[:3]

                names[group_name.strip().upper()] = names.get(group_name.strip().upper(), []) + [netbios_service.strip()]

            except Exception:

                pass

        if not names:

            return False

        else:

            return hackersh.objects.RemoteSessionContext(context, **{'PROTO': 'UDP', 'PORT': '137', 'SERVICE': 'NETBIOS-NS', 'NETBIOS-NS': {'NAMES': names}})

    # Consts

    DEFAULT_FILENAME = "nbtscan"

    DEFAULT_OUTPUT_OPTIONS = "-v -h -q -s ,"

    DEFAULT_FILTER = DEFAULT_QUERY = "context['IPV4_ADDRESS']"
