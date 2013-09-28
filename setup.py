#!/usr/bin/env python
#
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

try:

    import setuptools

except ImportError:

    from distribute_setup import use_setuptools

    use_setuptools()

    import setuptools


import sys


# Functions

def _safe_get_version():

    tmp_globals = {}

    # Importing _version.py may raise ImportError due to missing dependencies

    execfile('hackersh/_version.py', tmp_globals)

    version = tmp_globals['__version__']

    return version


# Entry Point

if __name__ == "__main__":

    dependencies = ['pythonect>=0.6.0', 'networkx>=1.7', 'prettytable>=0.6.1', 'netaddr>=0.7.10', 'pyparsing<=1.5.7', 'xerox>=0.3.1']

    major, minor = sys.version_info[:2]

    python_27 = (major > 2 or (major == 2 and minor >= 7))

    # < Python 2.7 ?

    if not python_27:

        # Python 2.6

        dependencies = dependencies + ['argparse>=1.2.1']

    setupconf = dict(
        name='Hackersh',
        version=_safe_get_version(),
        author='Itzik Kotler',
        author_email='xorninja@gmail.com',
        url='http://www.hackersh.org/',
        license='GPLv2+',
        description='Hackersh ("Hacker Shell") is a free and open source command-line shell and scripting language designed especially for security testing. Written in Python and uses Pythonect as its scripting engine, hackersh helps IT security professionals simulate real-world attacks and conduct penetration tests.',

        long_description=open('README.rst').read(),

        scripts=['bin/hackersh'],
        data_files=[('', ['COPYING'])],
        packages=setuptools.find_packages(),

        classifiers=[
            'Development Status :: 4 - Beta',
            'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
        ],

        install_requires=dependencies,

        zip_safe=False,

    )

    setuptools.setup(**setupconf)
