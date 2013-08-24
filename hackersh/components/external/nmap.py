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

import hackersh.objects


# Metadata

__author__ = "Itzik Kotler <xorninja@gmail.com>"
__version__ = "0.1.1"


# Implementation

class Nmap(hackersh.objects.ExternalComponentFileOutput):

    # XML Parser(s)

    class NmapXMLOutputHandler(hackersh.objects.XMLOutputHandler):

        def startElement(self, name, attrs):

            # i.e. <port protocol="tcp" portid="22"><state state="open" reason="syn-ack" reason_ttl="64"/><service name="ssh" method="table" conf="3" /></port>

            if name == "port":

                self._open = False

                self._portid = str(attrs['portid']).upper()

                self._protocol = str(attrs['protocol']).upper()

            # i.e. <state state="open" reason="syn-ack" reason_ttl="64"/>

            if name == "state":

                if attrs['state'] == 'open':

                    self._open = True

            # i.e. <service name="ssh" method="table" conf="3" />

            if name == "service":

                self._service = str(attrs['name']).upper()

        def endElement(self, name):

            if name == "port" and self._open:

                spinoffs = []

                # 'HTTP-PROXY' => 'HTTP' Spinoff.

                if self._service == 'HTTP-PROXY':

                    spinoffs.extend([{"PROTO": self._protocol.upper(), "PORT": self._portid, "SERVICE": 'HTTP'}])

                # PORT is already set, but with a different SERVICE? Spinoff.

                if self._context["PORT"] == self._portid \
                    and self._context['PROTO'] == self._protocol.upper() \
                    and self._context['SERVICE'] != self._service and self._service != 'HTTP-PROXY':

                    # "AS IT IS" Spinoff.

                    spinoffs.extend([{}])

                # i.e. {'PORT': 22, 'SERVICE': 'SSH'}

                spinoffs.extend([{'PROTO': self._protocol.upper(), 'PORT': self._portid, 'SERVICE': self._service}])

                for entry in spinoffs:

                    # Context per entry

                    self._output.append(entry)

        def endDocument(self):

            if not self._output:

                self._output.append(self._context)

    # Consts

    DEFAULT_FILENAME = "nmap"

    DEFAULT_OUTPUT_OPTIONS = "-oX"

    DEFAULT_QUERY = DEFAULT_FILTER = "IPV4_ADDRESS or HOSTNAME"
