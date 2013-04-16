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
import re
import os


# https://twistedmatrix.com/trac/browser/tags/releases/twisted-8.2.0/twisted/python/procutils.py

def which(name, flags=os.X_OK):

    result = []

    exts = filter(None, os.environ.get('PATHEXT', '').split(os.pathsep))

    path = os.environ.get('PATH', None)

    if path is None:

        return []

    for p in os.environ.get('PATH', '').split(os.pathsep):

        p = os.path.join(p, name)

        if os.access(p, flags):
            result.append(p)

        for e in exts:

            pext = p + e

            if os.access(pext, flags):
                result.append(pext)

    return result


def get_version():

    version = "0.0.0.dev0"

    try:

        git = subprocess.Popen(['git', 'describe'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        git.stderr.close()

        git_output = git.stdout.readlines()[0]

        git_ver = re.match('^\w+(?P<MAJOR>\d+)\.(?P<MINOR>\d+)(\.(?P<MICRO>\d+)(\-(?P<POST>\d+))?)?', git_output)

        if git_ver is not None:

            # MAJOR.MINOR

            version = git_ver.group('MAJOR') + '.' + git_ver.group('MINOR')

            if git_ver.groupdict('MICRO') is not None:

                # MAJOR.MINOR.MICRO

                version = version + '.' + git_ver.group('MICRO')

                if git_ver.groupdict('POST') is not None:

                    # MAJOR.MINOR.MICRO-POST

                    version = version + '.post' + git_ver.group('POST')

    except Exception:

        pass

    return version
