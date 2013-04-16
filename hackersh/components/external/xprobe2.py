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
__version__ = "0.1.0"


# Implementation

class Xprobe2(hackersh.objects.ExternalComponentFileOutput):

    # XML Parser(s)

    class Xprobe2XMLOutputHandler(hackersh.objects.XMLOutputHandler):

        def startDocument(self):

            self._read_content = False

            self._os_guess = []

        def startElement(self, name, attrs):

            #   <os_guess>
            #       <primary probability="100" unit="percent"> "Linux Kernel 2.4.30" </primary>
            #       <secondary probability="100" unit="percent"> "Linux Kernel 2.4.29" </secondary>
            #       <secondary probability="100" unit="percent"> "Linux Kernel 2.4.28" </secondary>
            #       <secondary probability="100" unit="percent"> "Linux Kernel 2.4.27" </secondary>
            #       <secondary probability="100" unit="percent"> "Linux Kernel 2.4.26" </secondary>
            #       <secondary probability="100" unit="percent"> "Linux Kernel 2.4.25" </secondary>
            #       <secondary probability="100" unit="percent"> "Linux Kernel 2.4.24" </secondary>
            #       <secondary probability="100" unit="percent"> "Linux Kernel 2.4.19" </secondary>
            #       <secondary probability="100" unit="percent"> "Linux Kernel 2.4.20" </secondary>
            #       <secondary probability="100" unit="percent"> "Linux Kernel 2.4.21" </secondary>
            #    </os_guess>

            if name == "primary" or name == "secondary":

                self._entry = {}

                self._read_content = True

        def characters(self, content):

            if self._read_content:

                self._entry.update({"OS": str(content).replace('"', '').strip()})

        def endElement(self, name):

            if name == "primary" or name == "secondary":

                self._os_guess.append(hackersh.objects.RemoteSessionContext(self._context, **self._entry))

                self._read_content = False

        def endDocument(self):

            if not self._os_guess:

                self._output.append(self._context)

            else:

                for entry in self._os_guess:

                    self._output.append(entry)

    # Consts

    DEFAULT_FILENAME = "xprobe2"

    DEFAULT_OUTPUT_OPTIONS = "-X -o"

    DEFAULT_QUERY = DEFAULT_FILTER = "context['HOSTNAME'] or context['IPV4_ADDRESS']"
