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

# Version

try:

    from _version import __version__

    # Clean up namespace

    del _version

except ImportError as e:

    from util import get_version

    __version__ = get_version()

    # Clean up namespace

    del e, get_version, util


# API

try:

    from objects import *

except ImportError as e:

    # When imported by setup.py, it's expected that not all the dependencies will be there

    pass
