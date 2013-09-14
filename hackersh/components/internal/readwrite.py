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

import networkx
import networkx.readwrite.json_graph
import os
import os.path


# Local imports

import hackersh.components.internal


# Metadata

__author__ = "Itzik Kotler <xorninja@gmail.com>"
__version__ = "0.1.0"


#############
# Functions #
#############

def _write_json_graph(graph, path):
    """Write graph in JSON format to path"""

    return open(path, 'w').write(networkx.readwrite.json_graph.dumps(graph))


def _read_json_graph(path):
    """Read a JSON-encoded graph from path"""

    return networkx.readwrite.json_graph.loads(open(path, 'r').read())


###################
# Implementations #
###################

class Read(hackersh.components.internal.InternalComponent):
    """Read Context from a File. File Type is based on the File Extension. Supported File Formats are: .gexf, .gml, .pickle, .graphml, .json, .leda, .yaml, .pajek, and .dot"""

    def run(self, argv, context):

        _new_context = False

        # *args -> []

        argv = list(argv)

        argv[0] = os.path.expanduser(argv[0])

        if not os.access(argv[0], os.R_OK):

            # This will raise IOError

            open(argv[0], 'r')

        ext = os.path.splitext(argv[0])[-1].lower()

        self.logger.debug('Reading Context from %s As %s Format' % (argv[0], ext.upper()))

        _reader_fcn = self._EXTENSION_TO_READER.get(ext, False)

        if _reader_fcn:

            _graph = _reader_fcn(argv[0])

            _new_context = hackersh.components.Context(_graph)

        return _new_context

    # Const

    _EXTENSION_TO_READER = {
        '.gexf': networkx.read_gexf,
        '.gml': networkx.read_gml,
        '.pickle': networkx.read_gpickle,
        '.graphml': networkx.read_graphml,
        '.json': _read_json_graph,
        '.leda': networkx.read_leda,
        '.yaml': networkx.read_yaml,
        '.pajek': networkx.read_pajek,
        '.dot': networkx.read_dot
    }


class Write(hackersh.components.internal.InternalComponent):
    """Write Context to a File. File Type is based on the File Extension. Supported File Formats are: .gexf, .gml, .pickle, .graphml, .json, .yaml, .pajek, and .dot"""

    def run(self, argv, context):

        # *args -> []

        argv = list(argv)

        argv[0] = os.path.expanduser(argv[0])

        if os.access(argv[0], os.F_OK):

            if not os.access(argv[0], os.W_OK):

                # This will raise IOError

                open(argv[0], 'w')

        ext = os.path.splitext(argv[0])[-1].lower()

        self.logger.debug('Writing Context to %s As %s Format' % (argv[0], ext.upper()))

        _writer_fcn = self._EXTENSION_TO_WRITER.get(ext, False)

        if _writer_fcn:

            _writer_fcn(context.as_graph(), argv[0])

        return context

    # Const

    _EXTENSION_TO_WRITER = {
        '.gexf': networkx.write_gexf,
        '.gml': networkx.write_gml,
        '.pickle': networkx.write_gpickle,
        '.graphml': networkx.write_graphml,
        '.json': _write_json_graph,
        '.yaml': networkx.write_yaml,
        '.pajek': networkx.write_pajek,
        '.dot': networkx.write_dot
    }


class write_all(Write):
    """Write All Contexts to File. File Type is based on the File Extension. See `write` Component Information for a List of Supported File Formats"""

    def run(self, argv, context):

        if isinstance(context, list):

            if len(context) > 1:

                context = reduce(lambda x, y: x + y if isinstance(x, hackersh.components.Context) else y + x, context)

        return Write.run(self, argv, context)
