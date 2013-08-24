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
import HTMLParser
import re
import networkx
import pythonect.internal._graph
import copy
import pprint


# Local imports

import log
import miscellaneous
import exceptions


# Component Classes

class Component(object):

    def __init__(self, *args, **kwargs):

        # Save for __call__()

        self._args = args

        self._kwargs = kwargs

        self.logger = log.logging.getLogger(self.__class__.__name__.lower())

        # Debug?
        if kwargs.get('debug', False):

            self.logger.setLevel(log.logging.DEBUG)

        self.logger.debug('Initialized %s with args = %s and kwargs = %s' % (repr(self), args, kwargs))

    # Application Binary Interface-like

    def run(self, argv, context):

        return_value = []

        self.logger.debug('In __run__ and calling %s' % self.main)

        entry_or_entries = self.main(argv, context)

        self.logger.debug('%s Returned:\n%s' % (self.main, pprint.pformat(entry_or_entries)))

        if entry_or_entries:

            if isinstance(entry_or_entries, list):

                result_id = 0

                for entry in entry_or_entries:

                    entry_key = self.__class__.__name__.lower() + "_result_#" + str(result_id)

                    self.logger.debug('Pushing %s = %s to return_value List' % (entry_key, entry))

                    return_value.append(context.push(entry_key, entry))

                    self.logger.debug('Pushed!')

                    result_id += 1

            elif isinstance(context, types.GeneratorType):

                # TODO: Don't iterate Generator, wrap it with another Generator

                pass

            else:

                if entry_or_entries == context:

                    self.logger.debug('%s == %s, Thus, return_value List will be equal: [True]' % (entry_or_entries, repr(context)))

                    return_value.append(True)

                else:

                    # return_value.append(context.push(self.__class__.__name__.lower(), entry_or_entries))

                    self.logger.debug('Pushing %s = %s, return_list will be equal This Push Only' % (self.__class__.__name__.lower(), entry_or_entries))

                    return_value = context.push(self.__class__.__name__.lower(), entry_or_entries)

        # False or Empty List (i.e. [])

        else:

            self.logger.debug('entry_or_entries is False? return_value List will be equal: [False]')

            return_value.append(False)

        self.logger.debug('Returning from __run__ with %s' % pprint.pformat(return_value))

        return return_value

    def __call__(self, arg):

        retval = None

        context = arg

        self.logger.debug('In __call__ with %s' % pprint.pformat(repr(context)))

        if not eval(self._kwargs.get('filter', self.DEFAULT_FILTER), {}, context):

                self.logger.debug('Filter """%s""" is False' % self._kwargs.get('filter', self.DEFAULT_FILTER))

                return False

                # raise exceptions.HackershError(context, "%s: not enough data to start" % self.__class__.__name__.lower())

        self.logger.debug('Filter """%s""" is True' % self._kwargs.get('filter', self.DEFAULT_FILTER))

        component_args_as_str = eval(self._kwargs.get('query', self.DEFAULT_QUERY), {}, context)

        self.logger.debug('Query Result = """%s"""' % component_args_as_str)

        argv = []

        try:

            argv = miscellaneous.shell_split(self._args[0] + ' ' + component_args_as_str)

        except IndexError:

            try:

                argv = miscellaneous.shell_split(component_args_as_str)

            except Exception:

                # "AS IT IS"

                argv = [component_args_as_str]

        self.logger.debug('Running with argv = %s and context = %s' % (argv, repr(context)))

        retval = self.run(argv, context)

        self.logger.debug('Returning from __call__')

        return retval


class RootComponent(Component):

    def __call__(self, arg):

        argv = list(self._args) or [arg]

        context = Context(root_name=arg.__class__.__name__ + '_' + str(arg).encode('base64').strip(), root_value={'NAME': str(arg)})

        self.logger.debug('New context = %s ; root = %s' % (repr(context), context._graph.graph['prefix'][:-1]))

        self.logger.debug('In __call__ with %s' % pprint.pformat(repr(context)))

        self.logger.debug('Running with argv = %s and context = %s' % (argv, repr(context)))

        retval = self.run(argv, context)

        self.logger.debug('Returning from __call__ with %s' % pprint.pformat(retval))

        return retval


class InternalComponent(Component):

    pass


class ExternalComponent(Component):

    def __init__(self, *args, **kwargs):

        Component.__init__(self, *args, **kwargs)

        self.DEFAULT_STDIN_BUFFER = None

    def _execute(self, argv, context):

        raise NotImplementedError

    def main(self, argv, context):

        filename = self._kwargs.get('filename', self.DEFAULT_FILENAME)

        self.logger.debug('External Application Filename = ' + filename)

        path = miscellaneous.which(filename)[:1]

        if not path:

            self.logger.debug("NO PATH!")

            raise exceptions.HackershError(context, "%s: command not found" % self._kwargs.get('filename', self.DEFAULT_FILENAME))

        self.logger.debug('External Application Path = ' + path[0])

        return self._processor(context, self._execute(path + argv, context))

    def _processor(self, context, data):

        raise NotImplementedError


class ExternalComponentReturnValueOutput(ExternalComponent):

    def _execute(self, argv, context):

        cmd = argv[0] + ' ' + self._kwargs.get('output_opts', self.DEFAULT_OUTPUT_OPTIONS) + " " + ' '.join(argv[1:])

        self.logger.debug('Shell Command = ' + cmd)

        p = subprocess.Popen(miscellaneous.shell_split(cmd), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        p.wait()

        return p.returncode


class ExternalComponentStreamOutput(ExternalComponent):

    def __init__(self, *args, **kwargs):

        ExternalComponent.__init__(self, *args, **kwargs)

        self._handlers = []

        # Auto-discovery of Output Handlers

        for name in dir(self):

            obj = getattr(self, name)

            if isinstance(obj, types.ClassType) and issubclass(obj, OutputHandler):

                self.logger.debug('Registering %s as Handler' % obj)

                self._handlers.append(obj)

        self.logger.debug('Handlers = %s' % self._handlers)

    def _execute(self, argv, context):

        tmpfile = tempfile.NamedTemporaryFile(delete=False)

        fname = tmpfile.name

        data = ""

        try:

            cmd = argv[0] + ' ' + self._kwargs.get('output_opts', self.DEFAULT_OUTPUT_OPTIONS) + " " + tmpfile.name + " " + ' '.join(argv[1:])

            self.logger.debug('Shell Command = ' + cmd)

            p = subprocess.Popen(miscellaneous.shell_split(cmd), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            (stdout_output, stderr_output) = p.communicate(input=self._kwargs.get('stdin', self.DEFAULT_STDIN_BUFFER))

            self.logger.debug('Standard Output (%d bytes) =\n"""%s"""' % (len(stdout_output), stdout_output))

            tmpfile.flush()

            os.fsync(tmpfile.fileno())

            tmpfile.close()

            tmpfile = open(fname, 'r')

            data = tmpfile.read()

            self.logger.debug('File Output (%d bytes) =\n"""%s"""' % (len(data), data))

        except Exception:

            os.remove(fname)

        return data

    def _processor(self, context, data):

        if data:

            self.logger.debug('Processing Data...')

            contexts = []

            # Do-while, try parse data with *every* possible Output Handler

            for handler in self._handlers:

                handler_instance = handler(context, contexts)

                self.logger.debug('Trying to Handle w/ %s' % handler_instance)

                handler_instance.parse(data)

            # No Output Handler could process output, unknown format?

            if not contexts:

                raise exceptions.HackershError(context, "%s: unable to parse: %s" % (self.__class__.__name__.lower(), str(data)))

            if isinstance(contexts, list) and len(contexts) == 1:

                contexts = contexts[0]

            return contexts

        else:

            self.logger.debug('No Data to Process!')

            return data


class ExternalComponentFileOutput(ExternalComponentStreamOutput):

    def _execute(self, argv, context):

        tmpfile = tempfile.NamedTemporaryFile(delete=False)

        fname = tmpfile.name

        data = ""

        try:

            cmd = argv[0] + ' ' + self._kwargs.get('output_opts', self.DEFAULT_OUTPUT_OPTIONS) + " " + tmpfile.name + " " + ' '.join(argv[1:])

            self.logger.debug('Shell Command = ' + cmd)

            p = subprocess.Popen(miscellaneous.shell_split(cmd), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            (stdout_output, stderr_output) = p.communicate(input=self._kwargs.get('stdin', self.DEFAULT_STDIN_BUFFER))

            self.logger.debug('Standard Output (%d bytes) =\n"""%s"""' % (len(stdout_output), stdout_output))

            tmpfile.flush()

            os.fsync(tmpfile.fileno())

            tmpfile.close()

            tmpfile = open(fname, 'r')

            data = tmpfile.read()

            self.logger.debug('File Output (%d bytes) =\n"""%s"""' % (len(data), data))

        except Exception as e:

            self.logger.exception(e)

            os.remove(fname)

        return data


class ExternalComponentStdoutOutput(ExternalComponentStreamOutput):

    def _execute(self, argv, context):

        cmd = argv[0] + ' ' + self._kwargs.get('output_opts', self.DEFAULT_OUTPUT_OPTIONS) + " " + ' '.join(argv[1:])

        self.logger.debug('Shell Command = ' + cmd)

        p = subprocess.Popen(miscellaneous.shell_split(cmd), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        p_stdout = p.communicate(input=self._kwargs.get('stdin', self.DEFAULT_STDIN_BUFFER))[0]

        self.logger.debug('Standard Output (%d bytes) =\n"""%s"""' % (len(p_stdout), p_stdout))

        return p_stdout


# Datatype Classes

class OutputHandler:

    def __init__(self, context, output):

        self._context = context

        self._output = output

    def parse(self):

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

    def startDocument():
        pass

    def endDocument():
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


class Context(object):

    def __init__(self, graph=None, root_name=None, root_value={}):

        if graph is None:

            self._graph = pythonect.internal._graph.Graph()

            if root_name is not None:

                # New Graph

                self._graph.add_node(root_name, root_value)

                self._graph.graph['prefix'] = root_name + '.'

        else:

            # From `graph`

            self._graph = graph

    def as_graph(self):

        return self._graph

    def __iter__(self):

        # So Pythonect won't iter()ate us ...

        return None

    def __getitem__(self, key):

        return_value = False

        for node in self._graph.nodes():

            if key in self._graph.node[node]:

                return_value = self._graph.node[node][key]

        return return_value

    def _copy(self):

        return copy.deepcopy(self)

    def push(self, key, value):

        # Copy-on-Write

        new_ctx = self._copy()

        new_ctx._graph = new_ctx._graph.copy()

        new_ctx._graph.add_node(new_ctx._graph.graph['prefix'] + key, value)

        new_ctx._graph.add_edge(new_ctx._graph.nodes()[-2], new_ctx._graph.nodes()[-1])

        new_ctx._graph.graph['prefix'] = new_ctx._graph.nodes()[-1] + '.'

        return new_ctx

    def pop(self):

        self._graph.remove_node(self._graph.nodes()[-1])

        # TODO: Adjust self.graph['prefix'] ?

    def __add__(self, other):

        if other:

            return Context(networkx.compose(other._graph, self._graph))

        else:

            return self

    def __div__(self, other):

        return_value = Context()

        filter_expression = other

        # Generate all possible (read: simple) flows between every root_node and every terminal_node

        for root_node in [node for node, degree in self._graph.in_degree().items() if degree == 0]:

            for terminal_node in [node for node, degree in self._graph.out_degree().items() if degree == 0]:

                for simple_path in networkx.all_simple_paths(self._graph, root_node, terminal_node):

                    tmp_ctx = Context(pythonect.internal._graph.Graph(self._graph.subgraph(simple_path)))

                    # Is generated Graph passes `filter_expression`? Add to result Graph.

                    if eval(filter_expression, {}, tmp_ctx):

                        return_value += tmp_ctx

        # Graph of all possible root_node to terminal_node that passes `filter_expression`

        return return_value

    def __repr__(self):

        if self._graph and self._graph.nodes():

            return str(map(lambda x: self._graph.node[x], self._graph.nodes()))

        else:

            return object.__repr__(self)
