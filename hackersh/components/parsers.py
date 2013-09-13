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

import xml.sax
import csv
import HTMLParser
import re


###########
# Classes #
###########

class OutputHandler:

    def __init__(self, context, output):

        self._context = context

        self._output = output

    def parse(self, data):

        raise NotImplementedError


# Pseudo SAX Content Handler for Simple Regualr Expression Match Handler

class SimpleRegExHandler(OutputHandler):

    def parse(self, data):

        regex = re.compile(self.PATTERN)

        for match in regex.finditer(data):

            self._output.append(self._context.__class__(self._context, **match.groupdict()))

    PATTERN = ""


# Pseudo SAX Content Handler for Stdout Output

class StdoutOutputHandler(OutputHandler):

    def startDocument(self):
        pass

    def endDocument(self):
        pass

    def parse(self, data):

        self.startDocument()

        self.feed(data)

        self.endDocument()


# Pseudo SAX Content Handler for CSV

class CSVOutputHandler(OutputHandler):

    def parse(self, data):

        self.startDocument()

        for row in csv.reader(data.split('\n'), delimiter=self.delimiter, quotechar=self.quotechar):

            self.startRow(row)

            self.endRow()

        self.endDocument()

    delimiter = csv.excel.delimiter

    quotechar = csv.excel.quotechar


# Pseudo SAX Content Handler for HTML

class HTMLOutputHandler(OutputHandler, HTMLParser.HTMLParser):

    def __init__(self, context, output):

        HTMLParser.HTMLParser.__init__(self)

        self._context = context

        self._output = output

    def parse(self, data):

        self.startDocument()

        self.feed(data)

        self.endDocument()


class XMLOutputHandler(OutputHandler, xml.sax.handler.ContentHandler):

    def __init__(self, context, output):

        xml.sax.handler.ContentHandler.__init__(self)

        self._context = context

        self._output = output

    def parse(self, data):

        xml.sax.parseString(data, self)
