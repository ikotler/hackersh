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

import sys


# Local imports

import hackersh.components.internal
import hackersh.conio


# Metadata

__author__ = "Itzik Kotler <xorninja@gmail.com>"
__version__ = "0.1.0"


# Implementations

class special_print(hackersh.components.internal.InternalComponent):
    """Print Current Context/Flow to the Standard Output"""

    def main(self, argv, context):

        data = data = argv or context

        if isinstance(data, list) and len(data) == 1:

            data = data[0]

        if isinstance(data, hackersh.components.Context):

            data = hackersh.conio.draw_graph_horizontal(data)

        sys.stdout.write('\n' + str(data).strip() + '\n\n')

        sys.stdout.flush()

        return context

    DISPLAY_NAME = 'print'


class special_print_all(special_print):
    """Print All Contexts/Flows to the Standard Output"""

    def main(self, argv, context):

        data = argv or context

        if isinstance(data, list):

            if len(data) > 1:

                buf = ''

                ctx_tree = reduce(lambda x, y: x + y if isinstance(x, hackersh.components.Context) else y + x, data)

                for root_node in [node for node, degree in ctx_tree.as_graph().in_degree().items() if degree == 0]:

                    buf += '\n'.join(hackersh.conio.draw_graph_vertical(ctx_tree.as_graph(), root_node))

                    # Insert NL Between Root Nodes

                    buf += '\n'

                context = ctx_tree

            else:

                buf = data[0]

        return special_print.main(self, buf, context)

    DISPLAY_NAME = 'print_all'
