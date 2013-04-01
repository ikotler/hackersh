========
Hackersh
========

`Hackersh <https://www.hackersh.org>`_ ("Hacker Shell") is a shell (command interpreter) written in Python with Pythonect-like syntax, builtin security commands, and out of the box wrappers for various security tools.

Hello, world
------------

Here is the canonical "Hello, world" example program in Hackersh::

	"http://localhost" -> url -> nmap -> w3af

Wait, what? This is a a compacted but 100% complete implementation of a black-box web application vulnerability scanner

Installation
------------

There are a few ways to install Hackersh.

1. You can install directly from PyPI_ using ``easy_install`` or pip_::

        easy_install hackersh

   or::

        pip install hackersh

2. You can clone the git repository somewhere in your system::

        git clone git://github.com/ikotler/hackersh.git

   Then you should do following steps::

        cd hackersh
        python setup.py install

   Alternatively, if you use pip_, you can install directly from the git repository::

        pip install \
        	git+git://github.com/ikotler/hackersh.git@master#egg=Hackersh \
		-r https://github.com/ikotler/hackersh/raw/master/doc/requirements.txt

For any of the above methods, if you want to do a system-wide installation, you will have to do this with *root* permissions (e.g. using ``su`` or ``sudo``).

.. _PyPI: http://pypi.python.org/pypi/Hackersh/
.. _pip: http://www.pip-installer.org/

License
-------

Hackersh is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2, or (at your option) any later version.
