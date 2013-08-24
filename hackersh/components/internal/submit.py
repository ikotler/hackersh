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

# Local imports

import hackersh.components.internal


# Metadata

__author__ = "Itzik Kotler <xorninja@gmail.com>"
__version__ = "0.1.0"


# Implementation

class Submit(hackersh.components.internal.InternalComponent):

    def main(self, argv, context):

        br = argv[0]

        br.select_form(nr=0)

        for k, v in self._kwargs.iteritems():

            br[k] = v

        response = br.submit()

        return dict(BR_OBJECT=br, URL=response.geturl())

    DEFAULT_FILTER = DEFAULT_QUERY = "BR_OBJECT"
