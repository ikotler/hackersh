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
import os
import shlex
import pythonect
import networkx


# Local imports

import miscellaneous


def __quotes_wrap(list):

    new_list = []

    for e in list:

        new_list.append("'%s'" % e)

    return new_list


def __hackersh_preprocessor(source, sym_tbl):

    orig_source = source

    # i.e. nmap

    if source in sym_tbl and not isinstance(sym_tbl[source], types.FunctionType):

        source = "%s()" % source

    # i.e. /usr/bin/nmap or ./nmap

    if source.startswith('/') or source.startswith('./') or source.startswith('../'):

        expression_cmd = shlex.split(source)

        external_component_path = os.path.abspath(expression_cmd[0])

        external_component_name = os.path.splitext(os.path.basename(external_component_path))[0]

        external_component_kwargs = '**{}'

        # External binary? (i.e. /bin/ls)

        if external_component_name not in sym_tbl:

            if not os.path.isfile(external_component_path):

                external_component_path = miscellaneous.which(expression_cmd[0])[0]

                if not external_component_path:

                    print '%s: command not found' % expression_cmd[0]

                    return False

            external_component_kwargs = "**{'path':'%s'}" % external_component_path

            external_component_name = "system"

            external_component_args = "*(%s)" % ','.join(__quotes_wrap(expression_cmd[1:]) + [' '])

        source = "%s(%s, %s)" % (external_component_name, external_component_args, external_component_kwargs)

    # print '%s => %s' % (orig_source, source)

    return source


def _hackersh_graph_transform(graph, hackersh_locals):

    # TODO: XSLT?

    for node in graph:

        graph.node[node]['CONTENT'] = __hackersh_preprocessor(graph.node[node]['CONTENT'].strip(), hackersh_locals)

    return graph


def parse(source):

    return pythonect.parse(source)


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
