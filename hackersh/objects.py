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

import os
import tempfile
import subprocess
import types
import xml.sax
import csv
import shlex
import collections
import HTMLParser
import types


# Local imports

import log
import conio
import util


# Component Classes

class Component(object):

    def __init__(self, *args, **kwargs):

        self.DEFAULT_STDIN_BUFFER = None

        self._args = args

        self._kwargs = kwargs

        self.logger = log.logging.getLogger(self.__class__.__name__.lower())

        if 'debug' in kwargs:

            self.logger.setLevel(log.logging.DEBUG)

        self.logger.debug('Initialized %s with args = %s and kwargs = %s' % (repr(self), args, kwargs))

    def __call__(self, arg):

        context = arg

        if not eval(self._kwargs.get('filter', self.DEFAULT_FILTER), {'context': context}):

                self.logger.debug("Filter %s is False" % self._kwargs.get('filter', self.DEFAULT_FILTER))

                return False

        self.logger.debug("Filter %s is True" % self._kwargs.get('filter', self.DEFAULT_FILTER))

        component_args_as_str = eval(self._kwargs.get('query', self.DEFAULT_QUERY), {'context': context})

        argv = []

        try:

            argv = shlex.split(self._args[0] + ' ' + component_args_as_str)

        except IndexError:

            try:

                argv = shlex.split(component_args_as_str)

            except Exception:

                # "AS IT IS"

                argv = [component_args_as_str]

        self.logger.debug('Running with argv = %s and context = %s' % (argv, repr(context)))

        context = self.run(argv, context)

        if context:

            if isinstance(context, list):

                for _context in context:

                    # Update STACK

                    _context.update({'STACK': _context.get('STACK', []) + [self.__class__.__name__]})

            else:

                # Don't iterate Generator, wrap it with another Generator

                if isinstance(context, types.GeneratorType):

                    # TODO: Add support for Generaor

                    pass

                else:

                    context.update({'STACK': context.get('STACK', []) + [self.__class__.__name__]})

        return context

    # Application Binary Interface-like

    def run(self, argv, context):

        raise NotImplementedError


class RootComponent(Component):

    def __call__(self, arg):

        argv = list(self._args) or [arg]

        self.logger.debug('Running with argv = %s and context = None' % argv)

        context = self.run(argv, None)

        if context:

            if isinstance(context, list):

                for _context in context:

                     # Add 'ROOT' and 'STACK'

                    _context.update({'ROOT': _context.get('ROOT', argv[0]), 'STACK': [self.__class__.__name__] + _context.get('STACK', [])})

            else:

                context.update({'ROOT': context.get('ROOT', argv[0]), 'STACK': [self.__class__.__name__] + context.get('STACK', [])})

        return context


class InternalComponent(Component):

    pass


class ExternalComponent(Component):

    def _execute(self, argv, context):

        raise NotImplementedError

    def run(self, argv, context):

        return self._processor(context, self._execute(util.which(self._kwargs.get('filename', self.DEFAULT_FILENAME))[:1] + argv, context))

    def _processor(self, context, data):

        raise NotImplementedError


class ExternalComponentFileOutput(ExternalComponent):

    def __init__(self, *args, **kwargs):

        ExternalComponent.__init__(self, *args, **kwargs)

        self._handlers = []

        # Auto-discovery of Output Handlers

        for name in dir(self):

            obj = getattr(self, name)

            if isinstance(obj, types.ClassType) and issubclass(obj, OutputHandler):

                self._handlers.append(obj)

    def _execute(self, argv, context):

        tmpfile = tempfile.NamedTemporaryFile(delete=False)

        fname = tmpfile.name

        data = ""

        try:

            cmd = argv[0] + ' ' + self._kwargs.get('output_opts', self.DEFAULT_OUTPUT_OPTIONS) + " " + tmpfile.name + " " + ' '.join(argv[1:])

            self.logger.debug('CMD = ' + cmd)

            p = subprocess.Popen(shlex.split(cmd), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            (stdout_output, stderr_output) = p.communicate(input=self._kwargs.get('stdin', self.DEFAULT_STDIN_BUFFER))

            self.logger.debug(stdout_output)

            tmpfile.flush()

            os.fsync(tmpfile.fileno())

            tmpfile.close()

            tmpfile = open(fname, 'r')

            data = tmpfile.read()

            self.logger.debug('DATA (%d bytes) = %s' % (len(data), data))

        except Exception:

            os.remove(fname)

        return data

    def _processor(self, context, data):

        if data:

            contexts = []

            # Do-while, try parse data with *every* possible Output Handler

            for handler in self._handlers:

                handler_instance = handler(context, contexts)

                handler_instance.parse(data)

                if contexts:

                    break

            # No Output Handler could process output, unknown format?

            if not contexts:

                raise Exception("Unable to parse: " + str(data))

            return contexts

        else:

            return data


class ExternalComponentStdoutOutput(ExternalComponent):

    def _execute(self, argv, context):

        cmd = argv[0] + ' ' + self._kwargs.get('output_opts', self.DEFAULT_OUTPUT_OPTIONS) + " " + ' '.join(argv[1:])

        self.logger.debug('CMD = ' + cmd)

        p = subprocess.Popen(shlex.split(cmd), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        p_stdout = p.communicate(input=self._kwargs.get('stdin', self.DEFAULT_STDIN_BUFFER))[0]

        self.logger.debug('DATA (%d bytes) = %s' % (len(p_stdout), p_stdout))

        return p_stdout


class ExternalComponentReturnValueOutput(ExternalComponent):

    def _execute(self, argv, context):

        cmd = argv[0] + ' ' + self._kwargs.get('output_opts', self.DEFAULT_OUTPUT_OPTIONS) + " " + ' '.join(argv[1:])

        self.logger.debug('CMD = ' + cmd)

        p = subprocess.Popen(shlex.split(cmd), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        p.wait()

        return p.returncode


# Datatype Classes

class OutputHandler:

    def __init__(self, context, output):

        self._context = context

        self._output = output

    def parse(self):

        raise NotImplementedError


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


class SessionContext(collections.OrderedDict):

    def __getitem__(self, key):

        value = False

        try:

            # Case insensitive

            value = collections.OrderedDict.__getitem__(self, key.upper())

        except KeyError:

            pass

        return value


class RemoteSessionContext(SessionContext):

    def __init__(self, *args, **kwargs):

        SessionContext.__init__(self, *args, **kwargs)

    def _tree_str(self):

        # TCP / UDP ?

        if self['PROTO'] == 'TCP' or self['PROTO'] == 'UDP':

            return self['PORT'] + '/' + self['PROTO'].lower() + ' (' + self.get('SERVICE', '?') + ')'

        else:

            return ''

    def __str__(self):

        # Properties

        output = \
            '\n' + conio.draw_underline('Properties:') + '\n' + \
            conio.draw_dict_tbl(self, ["Property", "Value"], filter(lambda key: not key.startswith('_') and key != 'VULNERABILITIES', self.keys())) + '\n'

        # Vulnerabilities

        if 'VULNERABILITIES' in self:

            output = \
                output + '\n' + \
                conio.draw_underline('Vulnerabilities:') + '\n' + \
                conio.draw_static_tbl(self['VULNERABILITIES'], ["VULNERABILITY DESCRIPTION", "URL"], ["DESCRIPTION", "DESTINATION"]) + '\n'

        return output


class LocalSessionContext(SessionContext):

    pass


class SessionsTree(object):

    def __init__(self, children):

        self.children = []

        self.keys = collections.OrderedDict()

        # N

        if isinstance(children, list):

            # Remove False's

            self.children = filter(lambda x: not isinstance(x, bool), children)

        # 1

        elif not isinstance(children, bool):

            self.children.append(children)

        if self.children:

            children_roots = list(set([child.values()[0] for child in self.children]))

            # 1

            if len(children_roots) == 1:

                self.keys[children_roots[0]] = self

            # N

            else:

                for children_root in children_roots:

                    self.keys[children_root] = SessionsTree(filter(lambda child: child.values()[0] == children_root, self.children))

    def _tree_str(self):

        if self.keys:

            if len(self.keys) == 1:

                yield self.children[0].values()[0]

                last = self.children[-1] if self.children else None

                for child in self.children:

                    prefix = '  `-' if child is last else '  +-'

                    for line in child._tree_str().splitlines():

                        yield '\n' + prefix + line

                        prefix = '  ' if child is last else '  | '

                yield '\n'

            # N

            else:

                for key in self.keys.keys():

                    yield self.keys[key]

        else:

            yield "Error\n"

    def __str__(self):

        return reduce(lambda x, y: str(x) + str(y), self._tree_str())

    def __getitem__(self, key):

        return self.keys.get(key, False)
