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

import subprocess


# Local imports

import hackersh.components.internal


# Metadata

__author__ = "Itzik Kotler <xorninja@gmail.com>"
__version__ = "0.1.0"


# Implementation

class System(hackersh.components.internal.InternalComponent):
    """Pass a String to the Shell. This component uses the subprocess module available on the Python Standard Library to spawn processes"""

    def __call__(self, arg):

        if self._args[0]:

            # Command at __init__ and arg as stdin

            command = self._args[0]

            if isinstance(arg, basestring):

                stdin_buffer = arg

            else:

                stdin_buffer = ''

        else:

            # Command as arg, no stdin

            command = arg
            stdin_buffer = ''

        self.logger.debug('Executing Shell Command: %s' % arg)

        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)

        (stdout_output, stderr_output) = p.communicate(stdin_buffer)

        return str(stdout_output)
