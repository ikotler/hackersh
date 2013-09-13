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

import tempfile
import os
import subprocess
import shlex


# Local imports

import hackersh.components.external
import hackersh.components.parsers


# Metadata

__author__ = "Itzik Kotler <xorninja@gmail.com>"
__version__ = "0.1.1"


# Implementation

class W3af(hackersh.components.external.ExternalComponentFileOutput):
    """Framework to Find and Exploit Web Application Vulnerabilities. W3af is a Web Application Attack and Audit Framework which aims to identify and exploit all web application vulnerabilities"""

    class W3afHTMLOutputHandler(hackersh.components.parsers.HTMLOutputHandler):

        def startDocument(self):

            self._dups = {}

            self._data = ""

            self._export_data = False

            self._in_tr = False

            self._vulnerabilities = []

        def handle_starttag(self, tag, attrs):

            if self._in_tr:

                if tag == 'td' and attrs == [('class', 'default'), ('width', '80%')]:

                    self._export_data = True

            if tag == 'tr':

                self._in_tr = True

        def handle_endtag(self, tag):

            if tag == 'tr':

                self._in_tr = False

            if tag == 'td' and self._export_data:

                self._export_data = False

                if self._data.find('\nSeverity'):

                    details = self._data.split('\nSeverity')[0].split('URL : ')

                else:

                    details = self._data.split('URL : ')

                if details[0].find('.') != -1:

                    # Remove the 'This vulnerability was found in the request with id 484.'

                    details[0] = '.'.join(details[0].split('.')[:-2])

                if not details[0].strip() in self._dups:

                    self._vulnerabilities.append({'DESCRIPTION': details[0], 'DESTINATION': details[1]})

                    self._dups[details[0].strip()] = True

                self._data = ""

        def handle_data(self, data):

                if self._export_data:

                    self._data = self._data + data

        def endDocument(self):

            self._output.append({'VULNERABILITIES': self._vulnerabilities})

#    class W3afCSVOutputHandler(hackersh.components.parsers.CSVOutputHandler):
#
#        def startDocument(self):
#
#            self._vulnerabilities = []
#
#        # i.e. Cross site scripting vulnerability,GET,http://192.168.1.108:8008/feed.gtl?uid=<SCrIPT>alert("flgC")</SCrIPT>,uid,uid=%3CSCrIPT%3Ealert%28%22flgC%22%29%3C%2FSCrIPT%3E,[1499],|Cross Site Scripting was found at: "http://192.168.1.108:8008/feed.gtl", using HTTP method GET. The sent data was: "uid=%3CSCrIPT%3Ealert%28%22flgC%22%29%3C%2FSCrIPT%3E". This vulnerability affects ALL browsers. This vulnerability was found in the request with id 1499.|
#
#        def startRow(self, row):
#
#            try:
#
#                (desc, method, url) = row[:3]
#
#                self._vulnerabilities.append({'DESCRIPTION': desc, 'DESTINATION': url})
#
#            except Exception:
#
#                pass
#
#        def endRow(self):
#
#            pass
#
#        def endDocument(self):
#
#            self._output.append(hackersh.objects.RemoteSessionContext(self._context, **{'VULNERABILITIES': self._context.get('VULNERABILITIES', []) + self._vulnerabilities}))

    # Custom _execute

    def _execute(self, argv, context):

        if len(argv) < 2:

            return False

        tmp_script_file = tempfile.NamedTemporaryFile()

        tmp_output_file = tempfile.NamedTemporaryFile()

        tmp_input_csv_file = tempfile.NamedTemporaryFile()

        tmp_cj_file = tempfile.NamedTemporaryFile()

        url = argv[1]

        tmp_input_csv_file.write("GET,%s,''" % url)

        tmp_input_csv_file.flush()

        script_content = [
            "plugins",
            "output console, csv_file, textFile, htmlFile",
            "output config csv_file",
            "set output_file /tmp/output.csv",
            "back",
            "output config console",
            "set verbose False",
            "back",
            "output config textFile",
            "set httpFileName /tmp/output-http.txt",
            "set fileName /tmp/output.txt",
            "set verbose True",
            "back",
            "output htmlFile",
            "output config htmlFile",
            "set fileName %s" % tmp_output_file.name,
            "set verbose False",
            "back",
            "output config xmlFile",
            "set fileName /tmp/output.xml",
            "back",
            "back"
        ]

        # Cookies?

        cj = context['COOKIES']

        if cj:

            cj.save(tmp_cj_file.name, True, True)

            script_content.extend([
                "http-settings",
                "set cookieJarFile %s" % tmp_cj_file.name,
                "back"
            ])

            tmp_cj_file.flush()

            os.fsync(tmp_cj_file.fileno())

        # User-Agent?

        ua = context['USER-AGENT']

        if ua:

            script_content.extend([
                "http-settings",
                "set userAgent %s" % ua,
                "back",
            ])

        # Visited URL's?

        visited_urls_list = context['VISITED_URLS']

        if visited_urls_list:

            script_content.extend([
                "misc-settings",
                "set nonTargets %s" % ','.join(visited_urls_list),
                "back"
            ])

        script_content.extend([
            "plugins",
            "grep all, !pathDisclosure"
        ])

        if self._kwargs.get('step', False):

            script_content.extend([
                "discovery !all, allowedMethods, importResults",
                "discovery config importResults",
                "set input_csv %s" % tmp_input_csv_file.name,
                "back"
            ])

        else:

            script_content.extend([
                "discovery !all, allowedMethods, webSpider",
                "discovery config webSpider",
                "set onlyForward True",
                "back"
            ])

        script_content.extend([
            "audit all, !xsrf",
            "bruteforce all",
            "audit config xss",
            "set numberOfChecks 15",
            "back",
            "back",
            "target",
            "set target %s" % url,
            "back",
            "start",
            "exit"
        ])

        self.logger.debug('Script Output:\n%s' % '\n'.join(script_content))

        tmp_script_file.write('\n'.join(script_content))

        tmp_script_file.flush()

        os.fsync(tmp_script_file.fileno())

        cmd = argv[0] + ' -s ' + tmp_script_file.name

        self.logger.debug('Invoking Popen w/ %s' % cmd)

        p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        hackersh.components.external._async_communicate(p, None, self.logger)

        tmp_output_file.flush()

        os.fsync(tmp_output_file.fileno())

        app_output = tmp_output_file.read()

        self.logger.debug('Application-specific Output:\n %s' % app_output)

        return app_output

    # Consts

    DEFAULT_FILENAME = "w3af_console"

    DEFAULT_FILTER = \
        "(SERVICE == 'HTTP' or SERVICE == 'HTTPS') and " \
        "(IPV4_ADDRESS or HOSTNAME) and " \
        "PROTO == 'TCP'"

    DEFAULT_QUERY = \
        "URL or (SERVICE.lower() + '://' + (IPV4_ADDRESS or HOSTNAME) + ':' + PORT)"
