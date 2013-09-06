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


# Local imports

import hackersh.miscellaneous


def __quotes_wrap(list):

    new_list = []

    for e in list:

        new_list.append("'%s'" % e)

    return new_list


def __hackersh_preprocessor(source, sym_tbl):

    if source.startswith('"""$'):

        # """$Hello World$"""' => 'Hello World'

        source = source[4:-4]

    tokens = shlex.split(source)

    # e.g. nmap

    if tokens[0] in sym_tbl and not isinstance(sym_tbl[tokens[0]], types.FunctionType):

        # i.e. nmap -sS -P0

        if len(tokens) > 1:

            source = "%s('%s')" % (tokens[0], ' '.join(tokens[1:]))

        # i.e. nmap

        else:

            source = "%s()" % source

    # i.e. /usr/bin/nmap or ./nmap

    elif tokens[0].startswith('/') or tokens[0].startswith('./') or tokens[0].startswith('../'):

        source = 'system(""" ' + source + ' """)'

    return source


def _hackersh_graph_transform(graph, hackersh_locals):

    # TODO: XSLT?

    for node in graph:

        graph.node[node]['CONTENT'] = __hackersh_preprocessor(graph.node[node]['CONTENT'].strip(), hackersh_locals)

    return graph


def __command_preprocessor(command):

    new_command = command = command.strip()

    if not command.startswith('[') and not command.endswith(']'):

        new_command = '"""$' + command + '$"""'

    return new_command


def parse(source):

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

    return pythonect.parse(new_source.strip())


def eval(source, locals_):

    return_value = None

    graph = None

    if source != "pass":

        if not isinstance(source, networkx.DiGraph):

            graph = parse(source)

        else:

            graph = source

        return_value = pythonect.eval(_hackersh_graph_transform(graph, locals_), locals_, {})

    return return_value
