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
__version__ = "0.1.2"


# Implementation

class SqlMap(hackersh.components.external.ExternalComponentStdoutOutput):

    # ---
    # Place: GET
    # Parameter: id
    #     Type: error-based
    #     Title: MySQL >= 5.0 AND error-based - WHERE or HAVING clause
    #     Payload: id=vGep' AND (SELECT 4752 FROM(SELECT COUNT(*),CONCAT(0x3a79706f3a,(SELECT (CASE WHEN (4752=4752) THEN 1 ELSE 0 END)),0x3a7a74783a,FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.CHARACTER_SETS GROUP BY x)a) AND 'ZzRA'='ZzRA&Submit=Submit
    #
    #     Type: UNION query
    #     Title: MySQL UNION query (NULL) - 2 columns
    #     Payload: id=vGep' LIMIT 1,1 UNION ALL SELECT CONCAT(0x3a79706f3a,0x4f674d774c6351717853,0x3a7a74783a), NULL#&Submit=Submit
    #
    #     Type: AND/OR time-based blind
    #     Title: MySQL < 5.0.12 AND time-based blind (heavy query)
    #     Payload: id=vGep' AND 7534=BENCHMARK(5000000,MD5(0x6d704e4c)) AND 'eALp'='eALp&Submit=Submit
    # ---

    class SqlMapStdoutOutputHandler(hackersh.components.parsers.StdoutOutputHandler):

        def startDocument(self):

            self._vulnerabilities = []

        def feed(self, data):

            for vuln_parameter in data.split('---'):

                if vuln_parameter.startswith('\nPlace'):

                    entry = {}

                    for line in vuln_parameter.split('\n'):

                        if line.find(':') == -1:

                            if entry:

                                # Fixup: if GET && Append URL to NAMELINK Value

                                if entry['Place'] == 'GET':

                                    entry['DESTINATION'] = self._context['URL'] + entry['DESTINATION']

                                self._vulnerabilities.append(dict(entry))

                            continue

                        (k, v) = line.lstrip().split(':')

                        entry[self.SQLMAP_KEYS_TO_GENERIC_WEB_VULN_KEYS.get(k, k)] = v.lstrip()

        def endDocument(self):

            self._output.append({'VULNERABILITIES': self._vulnerabilities})

        # Consts

        SQLMAP_KEYS_TO_GENERIC_WEB_VULN_KEYS = {'Title': 'DESCRIPTION', 'Payload': 'DESTINATION'}

    # Consts

    DEFAULT_FILENAME = ["sqlmap.py", "sqlmap"]

    DEFAULT_OUTPUT_OPTIONS = ''

    DEFAULT_FILTER = "URL"

    DEFAULT_QUERY = \
        "(('--cookie ' + str(COOKIES)) if COOKIES else '') + ' -u ' + URL"
