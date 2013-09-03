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


# Implementation

class print_(hackersh.components.internal.InternalComponent):

    def main(self, argv, context):

        buf = ""

        if isinstance(argv[0], hackersh.components.Context):

            for root_node in [node for node, degree in argv[0].as_graph().in_degree().items() if degree == 0]:

                buf += '\n'.join(hackersh.conio.draw_graph_vertical(argv[0].as_graph(), root_node))

                # Insert NL Between Root Nodes

                buf += '\n'

        elif isinstance(argv, list) and len(argv) == 1:

            buf = str(argv[0])

        else:

            buf = str(argv)

        sys.stdout.write(buf.strip() + '\n')

        sys.stdout.flush()

        return context
