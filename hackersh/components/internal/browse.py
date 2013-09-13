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

import cookielib
import mechanize
import tempfile
import os


# Local imports

import hackersh.components.internal


# Metadata

__author__ = "Itzik Kotler <xorninja@gmail.com>"
__version__ = "0.1.0"


# Implementation

class _MozillaCookieJarAsCommandLineArgument(cookielib.MozillaCookieJar):

    def __str__(self):

        cookies_arg = ""

        for cookie in self:

            cookies_arg += cookie.name + '=' + cookie.value + '; '

        return '"' + cookies_arg + '"'


class Browse(hackersh.components.internal.InternalComponent):

    def main(self, argv, context):

        _context = dict()

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

            _context['USER-AGENT'] = self._kwargs['ua']

        # Open URL

        response = br.open(url)

        response = br.open(url)

        if self._kwargs.get('dump', False):

            print response.read()

        return dict({'BR_OBJECT': br, 'URL': url, 'COOKIES': cj})

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
