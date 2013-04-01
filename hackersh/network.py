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
import urlparse
import cookielib
import subprocess
import shlex
import netaddr


# Local imports

import objects


# Classes

class IPv4_Address(objects.RootComponent):

    def run(self, argv, context):

        import socket

        _context = False

        try:

            socket.inet_aton(argv[0])

            _context = objects.RemoteSessionContext(IPV4_ADDRESS=argv[0])

        except socket.error, e:

            self.logger.debug('Caught exception %s' % str(e))

            # i.e. illegal IP address string passed to inet_aton

            pass

        return _context


class IPv4_Range(objects.RootComponent):

    def run(self, argv, context):

        contexts = []

        ipv4_addresses_gen = None

        try:

            # 192.168.1.0-255

            try:

                ipv4_addresses_gen = netaddr.IPGlob(argv[0])

            except netaddr.core.AddrFormatError as e:

                self.logger.debug('Caught exception %s' % str(e))

                try:

                    # 192.168.1.0/24

                    ipv4_addresses_gen = netaddr.IPNetwork(argv[0])

                except netaddr.core.AddrFormatError as e:

                    self.logger.debug('Caught exception %s' % str(e))

                    pass

            for ipv4_addr in ipv4_addresses_gen:

                contexts.append(objects.RemoteSessionContext(IPV4_ADDRESS=str(ipv4_addr)))

        except TypeError as e:

            pass

        return contexts


class Hostname(objects.RootComponent):

    def run(self, argv, context):

        import socket

        _context = False

        try:

            socket.gethostbyname(argv[0])

            _context = objects.RemoteSessionContext(HOSTNAME=argv[0])

        except socket.error as e:

            # i.e. socket.gaierror: [Errno -2] Name or service not known

            self.logger.debug('Caught exception %s' % str(e))

            pass

        return _context


class Nslookup(objects.RootComponent):

    def run(self, argv, context):

        import socket

        _context = False

        try:

            # i.e. '127.0.0.1'

            if isinstance(argv[0], basestring):

                _context = IPv4_Address().run([socket.gethostbyname(argv[0])], {})

            # i.e. RemoteSessionContext(HOSTNAME='localhost', ...)

            else:

                __context = objects.RemoteSessionContext(argv[0])

                _context = IPv4_Address().run([socket.gethostbyname(__context['HOSTNAME'])], {})

                _context.update(__context)

                # Turn HOSTNAME into a shadowed key

                __context['_HOSTNAME'] = __context['HOSTNAME']

                del __context['HOSTNAME']

        except socket.error as e:

            # i.e. socket.gaierror: [Errno -5] No address associated with hostname

            self.logger.debug('Caught exception %s' % str(e))

            pass

        return _context


class Ping(objects.ExternalComponentReturnValueOutput):

    def _processor(self, context, data):

        # i.e. Return Value == 0

        if data == 0:

            return objects.RemoteSessionContext(context, PINGABLE=True)

        return False

    # Consts

    DEFAULT_FILENAME = "ping"

    DEFAULT_OUTPUT_OPTIONS = "-c 3"

    DEFAULT_QUERY = DEFAULT_FILTER = "context['HOSTNAME'] or context['IPV4_ADDRESS']"


class URL(objects.RootComponent):

    def run(self, argv, context):

        _context = objects.RemoteSessionContext({'URL': argv[0]})

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

            __context = IPv4_Address().run([netloc], {})

            if not __context:

                __context = Hostname().run([netloc], {})

                if not __context:

                    # TODO: IPv6? MAC Address?

                    return __context

            # TODO: xrefer w/ URI scheme to make sure it's TCP, and not just assume

            _context.update(__context)

            _context.update({'PORT': netport, 'SERVICE': parse_result.scheme.upper(), 'PROTO': 'TCP'})

        return _context


class _MozillaCookieJarAsCommandLineArgument(cookielib.MozillaCookieJar):

    def __str__(self):

        cookies_arg = ""

        for cookie in self:

            cookies_arg += cookie.name + '=' + cookie.value + '; '

        return '"' + cookies_arg + '"'


class Browse(objects.InternalComponent):

    def run(self, argv, context):

        import mechanize

        url = argv[0]

        br = mechanize.Browser()

        cj = _MozillaCookieJarAsCommandLineArgument()

        already_existing_cj = context['COOKIES']

        # Duplicate Jar

        if already_existing_cj:

            tmp_cj_file = tempfile.NamedTemporaryFile()

            already_existing_cj.save(tmp_cj_file.name, True, True)

            tmp_cj_file.flush()

            os.fsync(tmp_cj_file.fileno())

            cj.load(tmp_cj_file.name, True, True)

        br.set_cookiejar(cj)

        # Browser Options

        br.set_handle_equiv(True)
        br.set_handle_redirect(True)
        br.set_handle_referer(True)
        br.set_handle_robots(False)
        br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

        if self._kwargs.get('ua', False):

            br.addheaders = [('User-agent', self._kwargs.get('ua'))]

            context['USER-AGENT'] = self._kwargs['ua']

        # Open URL

        response = br.open(url)

        response = br.open(url)

        if self._kwargs.get('dump', False):

            print response.read()

        return objects.RemoteSessionContext(context, **{'BR_OBJECT': br, 'URL': url, 'COOKIES': cj})

    DEFAULT_FILTER = \
        "(" \
        " (context['SERVICE'] == 'HTTP' or context['SERVICE'] == 'HTTPS') and " \
        " (context['HOSTNAME'] or context['IPV4_ADDRESS']) and " \
        " context['PROTO'] == 'TCP'" \
        ")" \
        "or" \
        "(" \
        " context['URL']" \
        ")"

    DEFAULT_QUERY = \
        "context['URL'] or (context['SERVICE'].lower() + '://' + (context['HOSTNAME'] or context['IPV4_ADDRESS']) + ':' + context['PORT'])"


class Submit(objects.InternalComponent):

    def run(self, argv, context):

        br = argv[0]

        br.select_form(nr=0)

        for k, v in self._kwargs.iteritems():

            br[k] = v

        response = br.submit()

        return objects.RemoteSessionContext(context, **{'BR_OBJECT': br, 'URL': response.geturl()})

    DEFAULT_FILTER = DEFAULT_QUERY = "context['BR_OBJECT']"


class Iterate_Links(objects.InternalComponent):

    def run(self, argv, context):

        contexts = []

        br = argv[0]

        for link in br.links():

            contexts.append(objects.RemoteSessionContext(context, URL=link.absolute_url))

        return contexts if contexts else False

    DEFAULT_FILTER = DEFAULT_QUERY = "context['BR_OBJECT']"


class W3af(objects.ExternalComponentFileOutput):

    class W3afHTMLOutputHandler(objects.HTMLOutputHandler):

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

            self._output.append(objects.RemoteSessionContext(self._context, **{'VULNERABILITIES': self._context.get('VULNERABILITIES', []) + self._vulnerabilities}))

#    class W3afCSVOutputHandler(objects.CSVOutputHandler):
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
#            self._output.append(objects.RemoteSessionContext(self._context, **{'VULNERABILITIES': self._context.get('VULNERABILITIES', []) + self._vulnerabilities}))

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

            pass

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

        tmp_script_file.write('\n'.join(script_content))

        tmp_script_file.flush()

        os.fsync(tmp_script_file.fileno())

        cmd = argv[0] + ' -s ' + tmp_script_file.name

        self.logger.debug('Invoking Popen w/ %s' % cmd)

        p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        (stdout_output, stderr_output) = p.communicate()

        tmp_output_file.flush()

        os.fsync(tmp_output_file.fileno())

        app_output = tmp_output_file.read()

        self.logger.debug('Application-specific Output:\n %s' % app_output)

        return app_output

    # Consts

    DEFAULT_FILENAME = "w3af_console"

    DEFAULT_FILTER = \
        "(context['SERVICE'] == 'HTTP' or context['SERVICE'] == 'HTTPS') and " \
        "(context['HOSTNAME'] or context['IPV4_ADDRESS']) and " \
        "context['PROTO'] == 'TCP'"

    DEFAULT_QUERY = \
        "context['URL'] or (context['SERVICE'].lower() + '://' + (context['HOSTNAME'] or context['IPV4_ADDRESS']) + ':' + context['PORT'])"


class SqlMap(objects.ExternalComponentStdoutOutput):

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

    def _processor(self, context, data):

        vulnerabilities = []

        for vuln_parameter in data.split('---'):

            if vuln_parameter.startswith('\nPlace'):

                entry = {}

                for line in vuln_parameter.split('\n'):

                    if line.find(':') == -1:

                        if entry:

                            # Fixup: if GET && Append URL to NAMELINK Value

                            if entry['Place'] == 'GET':

                                entry['DESTINATION'] = context['URL'] + entry['DESTINATION']

                            vulnerabilities.append(dict(entry))

                        continue

                    (k, v) = line.lstrip().split(':')

                    entry[self.SQLMAP_KEYS_TO_GENERIC_WEB_VULN_KEYS.get(k, k)] = v.lstrip()

        return objects.RemoteSessionContext(context, **{'VULNERABILITIES': context.get('VULNERABILITIES', []) + vulnerabilities})

    SQLMAP_KEYS_TO_GENERIC_WEB_VULN_KEYS = {'Title': 'DESCRIPTION', 'Payload': 'DESTINATION'}

    # Consts

    DEFAULT_FILENAME = "sqlmap.py"

    DEFAULT_OUTPUT_OPTIONS = ''

    DEFAULT_FILTER = "context['URL']"

    DEFAULT_QUERY = \
        "(context['COOKIES'] and '--cookie ' + str(context['COOKIES'])) + ' -u ' + context['URL']"


class Nikto(objects.ExternalComponentFileOutput):

    # XML Parser(s)

    class NiktoXMLOutputHandler(objects.XMLOutputHandler):

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

            self._output.append(objects.RemoteSessionContext(self._context, **{'VULNERABILITIES': self._context.get('VULNERABILITIES', []) + self._vulnerabilities}))

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


class Nmap(objects.ExternalComponentFileOutput):

    # XML Parser(s)

    class NmapXMLOutputHandler(objects.XMLOutputHandler):

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

                    self._output.append(objects.RemoteSessionContext(self._context, **entry))

        def endDocument(self):

            if not self._output:

                self._output.append(self._context)

    # Consts

    DEFAULT_FILENAME = "nmap"

    DEFAULT_OUTPUT_OPTIONS = "-oX"

    DEFAULT_QUERY = DEFAULT_FILTER = "context['HOSTNAME'] or context['IPV4_ADDRESS']"


class Amap(objects.ExternalComponentFileOutput):

    class AmapCSVOutputHandler(objects.CSVOutputHandler):

        def startDocument(self):

            self._entry_or_entries = []

        # i.e. test.old:21:tcp:open::ftp:220 ProFTPD 1.3.4a Server (Debian) [ffff127.0.0.1]\r\n500 GET not understood\r\n500 Invalid command try being more creative\r\n:"220 ProFTPD 1.3.4a Server (Debian) [::ffff:127.0.0.1]\r\n500 GET not understood\r\n500 Invalid command: try being more creative\r\n"

        def startRow(self, row):

            try:

                # IP_ADDRESS:PORT:PROTOCOL:PORT_STATUS:SSL:IDENTIFICATION:PRINTABLE_BANNER:FULL_BANNER

                (ip_addr, port, proto, port_status, ssl, identification) = row[:6]

                self._entry_or_entries.extend([{'PROTO': proto.upper(), 'PORT': str(int(port)), 'SERVICE': identification.upper()}])

            except Exception:

                pass

        def endRow(self):

            pass

        def endDocument(self):

            for entry in self._entry_or_entries:

                self._output.append(objects.RemoteSessionContext(self._context, **entry))

            if not self._output:

                self._output.append(self._context)

        # CSV Parsing Parameter

        delimiter = ':'

    # Consts

    DEFAULT_FILENAME = "amap"

    DEFAULT_OUTPUT_OPTIONS = "-m -o"

    DEFAULT_FILTER = \
        "(context['HOSTNAME'] or context['IPV4_ADDRESS']) and context['PROTO'] == 'TCP'"

    DEFAULT_QUERY = \
        "(context['HOSTNAME'] or context['IPV4_ADDRESS']) + ' ' + context['PORT']"


class Xprobe2(objects.ExternalComponentFileOutput):

    # XML Parser(s)

    class Xprobe2XMLOutputHandler(objects.XMLOutputHandler):

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

                self._os_guess.append(objects.RemoteSessionContext(self._context, **self._entry))

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


class Nbtscan(objects.ExternalComponentStdoutOutput):

    def _processor(self, context, data):

        import csv

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

            return objects.RemoteSessionContext(context, **{'PROTO': 'UDP', 'PORT': '137', 'SERVICE': 'NETBIOS-NS', 'NETBIOS-NS': {'NAMES': names}})

    # Consts

    DEFAULT_FILENAME = "nbtscan"

    DEFAULT_OUTPUT_OPTIONS = "-v -h -q -s ,"

    DEFAULT_FILTER = DEFAULT_QUERY = "context['IPV4_ADDRESS']"
