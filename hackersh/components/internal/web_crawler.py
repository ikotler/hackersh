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

import mechanize


# Local imports

import hackersh.components.internal
import hackersh.components.internal.url
import hackersh.components.internal.browse


# Metadata

__author__ = "Itzik Kotler <xorninja@gmail.com>"
__version__ = "0.1.0"


# Implementation

class Web_Crawler(hackersh.components.internal.InternalComponent):
    "Return a List of hyperlinks in a given Website. This component uses the mechanize module"

    def main(self, argv, context):

        contexts = []

        br = mechanize.Browser()

        (br, ignored) = hackersh.components.internal.browse._init_br(br, context)

        br.open(argv[0])

        for link in br.links():

            if self._kwargs.get('forward', False):

                if not link.absolute_url.startswith(argv[0]):

                    continue

            # Duplicate

            if link.absolute_url == argv[0] or link.absolute_url == argv[0] + '/':

                continue

            contexts.append(hackersh.components.internal.url.URL().main([link.absolute_url], {}))

        return contexts

    DEFAULT_FILTER = \
        "(" \
        " (SERVICE == 'HTTP' or SERVICE == 'HTTPS') and " \
        " (IPV4_ADDRESS or HOSTNAME) and " \
        " PROTO == 'TCP'" \
        ")" \
        "or" \
        "(" \
        " URL" \
        ")"

    DEFAULT_QUERY = \
        "URL or (SERVICE.lower() + '://' + (IPV4_ADDRESS or HOSTNAME) + ':' + PORT)"
