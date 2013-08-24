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
import types
import pprint
import networkx
import copy


# Hacks

import pythonect.internal._graph


# Local imports

import hackersh
import hackersh.log
import hackersh.miscellaneous


#############
# Functions #
#############

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

                            if obj != Component and issubclass(obj, Component):

                                instances[name.lower()] = obj

                                hackersh.log.logger.debug('Registering %s as %s' % (obj, name.lower()))

                        except TypeError:

                            pass

            except Exception as e:

                hackersh.log.logger.warn('Unable to register %s due to: %s' % (component_file, e))

                pass

    return instances

###########
# Classes #
###########

class Component(object):

    def __init__(self, *args, **kwargs):

        # Save for __call__()

        self._args = args

        self._kwargs = kwargs

        self.logger = hackersh.log.logging.getLogger(self.__class__.__name__.lower())

        # Debug?
        if kwargs.get('debug', False):

            self.logger.setLevel(hackersh.log.logging.DEBUG)

        self.logger.debug('Initialized %s with args = %s and kwargs = %s' % (repr(self), args, kwargs))

    # Application Binary Interface-like

    def run(self, argv, context):

        return_value = []

        self.logger.debug('In __run__ and calling %s' % self.main)

        entry_or_entries = self.main(argv, context)

        self.logger.debug('%s Returned:\n%s' % (self.main, pprint.pformat(entry_or_entries)))

        if entry_or_entries:

            if isinstance(entry_or_entries, list):

                result_id = 0

                for entry in entry_or_entries:

                    entry_key = self.__class__.__name__.lower() + "_result_#" + str(result_id)

                    self.logger.debug('Pushing %s = %s to return_value List' % (entry_key, entry))

                    return_value.append(context.push(entry_key, entry))

                    self.logger.debug('Pushed!')

                    result_id += 1

            elif isinstance(context, types.GeneratorType):

                # TODO: Don't iterate Generator, wrap it with another Generator

                pass

            else:

                if entry_or_entries == context:

                    self.logger.debug('%s == %s, Thus, return_value List will be equal: [True]' % (entry_or_entries, repr(context)))

                    return_value.append(True)

                else:

                    # return_value.append(context.push(self.__class__.__name__.lower(), entry_or_entries))

                    self.logger.debug('Pushing %s = %s, return_list will be equal This Push Only' % (self.__class__.__name__.lower(), entry_or_entries))

                    return_value = context.push(self.__class__.__name__.lower(), entry_or_entries)

        # False or Empty List (i.e. [])

        else:

            self.logger.debug('entry_or_entries is False? return_value List will be equal: [False]')

            return_value.append(False)

        self.logger.debug('Returning from __run__ with %s' % pprint.pformat(return_value))

        return return_value

    def __call__(self, arg):

        retval = None

        context = arg

        self.logger.debug('In __call__ with %s' % pprint.pformat(repr(context)))

        if not eval(self._kwargs.get('filter', self.DEFAULT_FILTER), {}, context):

                self.logger.debug('Filter """%s""" is False' % self._kwargs.get('filter', self.DEFAULT_FILTER))

                return False

                # raise exceptions.HackershError(context, "%s: not enough data to start" % self.__class__.__name__.lower())

        self.logger.debug('Filter """%s""" is True' % self._kwargs.get('filter', self.DEFAULT_FILTER))

        component_args_as_str = eval(self._kwargs.get('query', self.DEFAULT_QUERY), {}, context)

        self.logger.debug('Query Result = """%s"""' % component_args_as_str)

        argv = []

        try:

            argv = hackersh.miscellaneous.shell_split(self._args[0] + ' ' + component_args_as_str)

        except IndexError:

            try:

                argv = hackersh.miscellaneous.shell_split(component_args_as_str)

            except Exception:

                # "AS IT IS"

                argv = [component_args_as_str]

        self.logger.debug('Running with argv = %s and context = %s' % (argv, repr(context)))

        retval = self.run(argv, context)

        self.logger.debug('Returning from __call__')

        return retval


class RootComponent(Component):

    def __call__(self, arg):

        argv = list(self._args) or [arg]

        context = Context(root_name=arg.__class__.__name__ + '_' + str(arg).encode('base64').strip(), root_value={'NAME': str(arg)})

        self.logger.debug('New context = %s ; root = %s' % (repr(context), context._graph.graph['prefix'][:-1]))

        self.logger.debug('In __call__ with %s' % pprint.pformat(repr(context)))

        self.logger.debug('Running with argv = %s and context = %s' % (argv, repr(context)))

        retval = self.run(argv, context)

        self.logger.debug('Returning from __call__ with %s' % pprint.pformat(retval))

        return retval


class Context(object):

    def __init__(self, graph=None, root_name=None, root_value={}):

        if graph is None:

            self._graph = pythonect.internal._graph.Graph()

            if root_name is not None:

                # New Graph

                self._graph.add_node(root_name, root_value)

                self._graph.graph['prefix'] = root_name + '.'

        else:

            # From `graph`

            self._graph = graph

    def as_graph(self):

        return self._graph

    def __iter__(self):

        # So Pythonect won't iter()ate us ...

        return None

    def __getitem__(self, key):

        return_value = False

        for node in self._graph.nodes():

            if key in self._graph.node[node]:

                return_value = self._graph.node[node][key]

        return return_value

    def _copy(self):

        return copy.deepcopy(self)

    def push(self, key, value):

        # Copy-on-Write

        new_ctx = self._copy()

        new_ctx._graph = new_ctx._graph.copy()

        new_ctx._graph.add_node(new_ctx._graph.graph['prefix'] + key, value)

        new_ctx._graph.add_edge(new_ctx._graph.nodes()[-2], new_ctx._graph.nodes()[-1])

        new_ctx._graph.graph['prefix'] = new_ctx._graph.nodes()[-1] + '.'

        return new_ctx

    def pop(self):

        self._graph.remove_node(self._graph.nodes()[-1])

        # TODO: Adjust self.graph['prefix'] ?

    def __add__(self, other):

        if other:

            return Context(networkx.compose(other._graph, self._graph))

        else:

            return self

    def __div__(self, other):

        return_value = Context()

        filter_expression = other

        # Generate all possible (read: simple) flows between every root_node and every terminal_node

        for root_node in [node for node, degree in self._graph.in_degree().items() if degree == 0]:

            for terminal_node in [node for node, degree in self._graph.out_degree().items() if degree == 0]:

                for simple_path in networkx.all_simple_paths(self._graph, root_node, terminal_node):

                    tmp_ctx = Context(pythonect.internal._graph.Graph(self._graph.subgraph(simple_path)))

                    # Is generated Graph passes `filter_expression`? Add to result Graph.

                    if eval(filter_expression, {}, tmp_ctx):

                        return_value += tmp_ctx

        # Graph of all possible root_node to terminal_node that passes `filter_expression`

        return return_value

    def __repr__(self):

        if self._graph and self._graph.nodes():

            return str(map(lambda x: self._graph.node[x], self._graph.nodes()))

        else:

            return object.__repr__(self)
