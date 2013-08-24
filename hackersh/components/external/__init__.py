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

# Local imports

import hackersh.components
import hackersh.miscellaneous
import hackersh.exceptions


###########
# Classes #
###########

class ExternalComponent(hackersh.components.Component):

    def __init__(self, *args, **kwargs):

        hackersh.components.Component.__init__(self, *args, **kwargs)

        self.DEFAULT_STDIN_BUFFER = None

    def _execute(self, argv, context):

        raise NotImplementedError

    def main(self, argv, context):

        filename = self._kwargs.get('filename', self.DEFAULT_FILENAME)

        self.logger.debug('External Application Filename = ' + filename)

        path = hackersh.miscellaneous.which(filename)[:1]

        if not path:

            self.logger.debug("NO PATH!")

            raise hackersh.exceptions.HackershError(context, "%s: command not found" % self._kwargs.get('filename', self.DEFAULT_FILENAME))

        self.logger.debug('External Application Path = ' + path[0])

        return self._processor(context, self._execute(path + argv, context))

    def _processor(self, context, data):

        raise NotImplementedError


class ExternalComponentReturnValueOutput(ExternalComponent):

    def _execute(self, argv, context):

        cmd = argv[0] + ' ' + self._kwargs.get('output_opts', self.DEFAULT_OUTPUT_OPTIONS) + " " + ' '.join(argv[1:])

        self.logger.debug('Shell Command = ' + cmd)

        p = subprocess.Popen(hackersh.miscellaneous.shell_split(cmd), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        p.wait()

        return p.returncode


class ExternalComponentStreamOutput(ExternalComponent):

    def __init__(self, *args, **kwargs):

        ExternalComponent.__init__(self, *args, **kwargs)

        self._handlers = []

        # Auto-discovery of Output Handlers

        for name in dir(self):

            obj = getattr(self, name)

            if isinstance(obj, types.ClassType) and issubclass(obj, hackersh.components.parsers.OutputHandler):

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

            p = subprocess.Popen(hackersh.miscellaneous.shell_split(cmd), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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

                raise hackersh.exceptions.HackershError(context, "%s: unable to parse: %s" % (self.__class__.__name__.lower(), str(data)))

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

            p = subprocess.Popen(hackersh.miscellaneous.shell_split(cmd), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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

        p = subprocess.Popen(hackersh.miscellaneous.shell_split(cmd), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        p_stdout = p.communicate(input=self._kwargs.get('stdin', self.DEFAULT_STDIN_BUFFER))[0]

        self.logger.debug('Standard Output (%d bytes) =\n"""%s"""' % (len(p_stdout), p_stdout))

        return p_stdout

