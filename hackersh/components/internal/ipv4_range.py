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

import netaddr


# Local imports

import hackersh.components


# Metadata

__author__ = "Itzik Kotler <xorninja@gmail.com>"
__version__ = "0.1.0"


# Implementation

class IPv4_Range(hackersh.components.RootComponent):
    """Convert String to IPv4 Address Range"""

    def main(self, argv, context):

        _contexts = []

        ipv4_addresses_gen = None

        # 192.168.1.0-255

        try:

            ipv4_addresses_gen = netaddr.IPGlob(argv[0])

        except netaddr.core.AddrFormatError:

            # 192.168.1.0/24

            ipv4_addresses_gen = netaddr.IPNetwork(argv[0])

        for ipv4_addr in ipv4_addresses_gen:

            _contexts.append(dict(IPV4_ADDRESS=str(ipv4_addr)))

        # [dict(IPV4_ADDRESS="192.168.1.1"), dict(IPV4_ADDRESS="192.168.1.2"), ...]

        return _contexts
