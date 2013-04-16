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

import importlib
import glob
import os
import sys


# Local imports

import hackersh
import hackersh.log


def get_all_components(components_path):

    instances = {}

    # For each directory in components path

    for component_directory in components_path.split(os.path.pathsep):

        # Add component directory to path

        sys.path.insert(0, component_directory)

        components_list = glob.glob(component_directory + '/*.py')

        # For each *.py file in directory

        for component_file in components_list:

            component = os.path.splitext(os.path.basename(component_file))[0]

            try:

                current_module = importlib.import_module(component)

                for name in dir(current_module):

                    if not name.startswith('_'):

                        obj = getattr(current_module, name)

                        try:

                            if obj != hackersh.Component and issubclass(obj, hackersh.Component):

                                instances[name.lower()] = obj

                                hackersh.log.logger.debug('Registering %s as %s' % (obj, name.lower()))

                        except TypeError:

                            pass

            except Exception as e:

                hackersh.log.logger.warn('Unable to register %s due to: %s' % (component_file, e))

                pass

    return instances
