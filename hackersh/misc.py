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
import tempfile
import shlex


# Local imports

import objects


# Classes

class System(objects.Component):

    def __call__(self, arg):

        cmd = shlex.split(self._kwargs['path']) + list(self._args)

        self.logger.debug('Executing shell command %s' % ' '.join(cmd))

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)

        (stdout_output, stderr_output) = p.communicate(arg)

        return str(stdout_output)


class print_(objects.Component):

    def __call__(self, arg):

        import sys

        sys.stdout.write(str(arg) + '\n')

        sys.stdout.flush()

        return arg


class Null(objects.Component):

    def __call__(self, arg):

        return ''


class tmpfile(objects.Component):

    def __call__(self, arg):

        tfile = tempfile.NamedTemporaryFile(delete=False)

        print tfile.name

        tfile.write(str(arg))

        tfile.close()

        return ''


class Alert(objects.Component):

    def __call__(self, arg):

        return arg.__class__(arg, **{'VULNERABILITIES': arg.get('VULNERABILITIES', []) + [self._kwargs]})
