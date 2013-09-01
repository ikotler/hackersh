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

import urlparse


# Local imports

import hackersh.components
import hackersh.components.internal.ipv4_address
import hackersh.components.internal.hostname


# Metadata

__author__ = "Itzik Kotler <xorninja@gmail.com>"
__version__ = "0.1.0"


# Implementation

class URL(hackersh.components.RootComponent):

    def main(self, argv, context):

        _context = dict(URL=argv[0])

        parse_result = urlparse.urlparse(argv[0])

        if parse_result.scheme and parse_result.netloc:

            netloc = parse_result.netloc

            # i.e. http://localhost:8080

            try:

                (netloc, netport) = netloc.split(':')

            except ValueError:

            # i.e. http://localhost

                netport = '80'

            # i.e. http://locahost or http://127.0.0.1?

            try:

                __context = hackersh.components.internal.ipv4_address.IPv4_Address().main([netloc], {})

            except Exception:

                # TODO: IPv6? MAC Address?

                __context = hackersh.components.internal.hostname.Hostname().main([netloc], {})

            # TODO: xrefer w/ URI scheme to make sure it's TCP, and not just assume

            _context.update(__context)

            _context.update({'PORT': netport, 'SERVICE': parse_result.scheme.upper(), 'PROTO': 'TCP'})

        return _context
