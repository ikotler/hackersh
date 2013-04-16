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

class Nikto(hackersh.objects.ExternalComponentFileOutput):

    # XML Parser(s)

    class NiktoXMLOutputHandler(hackersh.objects.XMLOutputHandler):

        def startDocument(self):

            self._vulnerabilities = []

        def startElement(self, name, attrs):

            # <item id="999990" osvdbid="0" osvdblink="0_LINK" method="GET">
            # <description><![CDATA[Allowed HTTP Methods: GET, HEAD, POST, OPTIONS ]]></description>
            # <uri><![CDATA[/]]></uri>
            # <namelink><![CDATA[http://localhost:80/]]></namelink>
            # <iplink><![CDATA[http://127.0.0.1:80/]]></iplink>
            # </item>

            if name == "item":

                self._entry = {'OSVDBID': str(attrs['osvdbid'])}

        def characters(self, content):

            self._data = str(content)

        def endElement(self, name):

            if name == "item":

                self._entry['DESTINATION'] = self._entry['NAMELINK']

                self._vulnerabilities.append(dict(self._entry))

                self._entry = {}

            else:

                self._entry[str(name).upper()] = self._data

        def endDocument(self):

            self._output.append(hackersh.objects.RemoteSessionContext(self._context, **{'VULNERABILITIES': self._context.get('VULNERABILITIES', []) + self._vulnerabilities}))

    # Consts

    DEFAULT_FILENAME = "nikto"

    DEFAULT_STDIN_BUFFER = "n\n\n"

    DEFAULT_OUTPUT_OPTIONS = "-Format xml -o"

    DEFAULT_FILTER = \
        "(context['SERVICE'] == 'HTTP' or context['SERVICE'] == 'HTTPS') and " \
        "(context['HOSTNAME'] or context['IPV4_ADDRESS']) and " \
        "context['PROTO'] == 'TCP'"

    DEFAULT_QUERY = \
        "'-host ' + (context['HOSTNAME'] or context['IPV4_ADDRESS']) + ' -port ' + context['PORT']"
