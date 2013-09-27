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

import types
import shlex
import pythonect
import networkx
import logging


# Local imports

import hackersh.miscellaneous


_log = logging.getLogger(__name__)


def __quotes_wrap(list):

    new_list = []

    for e in list:

        new_list.append("'%s'" % e)

    return new_list


def __hackersh_preprocessor(source, sym_tbl):

    if source.startswith('"""$'):

        # """$Hello World$"""' => 'Hello World'

        source = source[4:-4]

    # If source is already graph, it won't go through parse(), thus .encode('utf8') is required.

    tokens = shlex.split(source.encode('utf8'))

    _log.debug('%s tokens are: %s' % (source, tokens))

    # FIX: shlex.split("write_all('/tmp/x.dot')") = ['write_all(/tmp/x.dot) => ['write_all', '/tmp/x.dot']

    if len(tokens) == 1 and tokens[0].find('(') != -1:

        tokens = map(lambda x: x if x.find('=') != -1 else "'" + x + "'", shlex.split(tokens[0].replace('(', ' ').replace(')', ' ')))

        _log.debug("Trying to split again, this time without '(') and ')'")

        _log.debug('%s tokens are: %s' % (source, tokens))

    # e.g. nmap

    if not tokens[0].startswith('_') and tokens[0] in sym_tbl and isinstance(sym_tbl[tokens[0]], (type, types.ClassType)) and issubclass(sym_tbl[tokens[0]], hackersh.Component):

        cls_name = tokens[0]

        _log.debug('cls_name = %s' % cls_name)

        # Alias?

        if tokens[0].lower() != sym_tbl[tokens[0]].__name__.lower():

            cls_name = 'alias_' + sym_tbl[tokens[0]].__name__.lower()

            _log.debug('Is Alias! New cls_name = %s' % cls_name)

        # i.e. nmap -sS -P0

        if len(tokens) > 1:

            # Reduce?

            if cls_name.endswith('_all'):

                _log.debug('%s is a (complex case of) Reduce Component!' % cls_name)

                source = "%s('%s', context=_!)" % (cls_name, ' '.join(tokens[1:]))

            else:

                source = "%s('%s')" % (cls_name, ' '.join(tokens[1:]))

        # i.e. nmap

        else:

            source = "%s()" % cls_name

            # Reduce?

            if cls_name.endswith('_all'):

                source += '(_!)'

                _log.debug('%s is a (simple case of) Reduce Component!' % cls_name)

    # i.e. /usr/bin/nmap or ./nmap

    elif tokens[0].startswith('/') or tokens[0].startswith('./') or tokens[0].startswith('../'):

        source = 'system(""" ' + source + ' """)'

    # e.g. _

    else:

        # AS IS

        pass

    return source


def _hackersh_graph_transform(graph, hackersh_locals):

    # TODO: XSLT?

    for node in graph:

        _log.debug('Before __hackersh_preprocessor, CONTENT = %s' % (graph.node[node]['CONTENT']))

        graph.node[node]['CONTENT'] = __hackersh_preprocessor(graph.node[node]['CONTENT'].strip(), hackersh_locals)

        _log.debug('After __hackersh_preprocessor, CONTENT = %s' % (graph.node[node]['CONTENT']))

    return graph


def __command_preprocessor(command):

    new_command = command = command.strip()

    if not command.startswith('[') and not command.endswith(']'):

        new_command = '"""$' + command + '$"""'

    return new_command


def parse(source):
    """Parse text-mode Hackersh scripting language into a directed graph (i.e. networkx.DiGraph)

    Args:
        source: A string representing text-based Hackersh code.

    Returns:
        A directed graph (i.e. networkx.DiGraph) of Hackersh symbols.

    Raises:
        SyntaxError: An error occurred parsing the code.
    """

    _log.debug('Calling parse WITH %s' % (source))

    command_buffer = ""
    depth = 0

    tokens = hackersh.miscellaneous.shell_split(source.encode('utf8'))

    new_source = ""

    ###############
    # Mini Parser #
    ###############

    for t in tokens:

        # 'Hello, world' -> print -> ...

        if t in ['|', '->'] and depth == 0:

            new_source += __command_preprocessor(command_buffer.strip()) + ' ' + t + ' '

            command_buffer = ""

        else:

            command_buffer += ' ' + t

            if t.startswith('[') or t.startswith('('):

                depth += 1

            if t.endswith(']') or t.endswith(']'):

                depth -= 1

    new_source += __command_preprocessor(command_buffer.strip())

    ('NEW_SOURCE = %s' % (new_source))

    return pythonect.parse(new_source.strip())


def eval(source, namespace):
    """Evaluate Hackersh code in the context of locals.

    Args:
        source: A string representing text-based Hackersh code or networkx.DiGraph instance()
        namespace: A dictionary with components.

    Returns:
        The return value is the result of the evaluated code.

    Raises:
        SyntaxError: An error occurred parsing the code.
    """

    return_value = None

    graph = None

    _log.debug('In eval with SOURCE = %s (%s)' % (source, repr(source)))

    if source != "pass":

        if not isinstance(source, networkx.DiGraph):

            graph = parse(source)

        else:

            graph = source

        return_value = pythonect.eval(_hackersh_graph_transform(graph, namespace), {'__IN_EVAL__': True}, namespace)

    return return_value
