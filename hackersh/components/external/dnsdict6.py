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

# Local imports

import hackersh.components.external
import hackersh.components.parsers


# Metadata

__author__ = "Itzik Kotler <xorninja@gmail.com>"
__version__ = "0.1.0"


# Implementation

class DnsDict6(hackersh.components.external.ExternalComponentStdoutOutput):

    class DnsDict6IPv4Output(hackersh.components.parsers.SimpleRegExHandler):

        PATTERN = "(?P<HOSTNAME>.*)\s+->\s+(?P<IPV4_ADDRESS>.*)"

    class DnsDict6IPv6Output(hackersh.components.parsers.SimpleRegExHandler):

        PATTERN = "(?P<HOSTNAME>.*)\s+=>\s+(?P<IPV6_ADDRESS>.*)"

    # Consts

    DEFAULT_FILENAME = "dnsdict6"

    DEFAULT_OUTPUT_OPTIONS = ''

    DEFAULT_QUERY = DEFAULT_FILTER = "DOMAIN"
