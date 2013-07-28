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
import shlex


def shell_split(s):
    lex = shlex.shlex(s)
    lex.quotes = '"'
    lex.whitespace_split = True
    lex.commenters = ''
    return list(lex)


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
