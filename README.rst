========
Hackersh
========

.. image:: https://badge.fury.io/py/Hackersh.png
    :target: http://badge.fury.io/py/Hackersh
    :alt: Latest version

.. image:: https://pypip.in/d/Hackersh/badge.png
    :target: https://crate.io/packages/Hackersh/
    :alt: Number of PyPI downloads

Homepage: `http://www.hackersh.org/ <http://www.hackersh.org/>`_

`Hackersh <http://www.hackersh.org>`_ ("Hacker Shell") is a free and open source command-line shell and scripting language designed especially for security testing. Written in Python and uses Pythonect as its scripting engine, hackersh helps IT security professionals simulate real-world attacks and conduct penetration tests.

Hello, world
------------

Here is the canonical "Hello, world" example program in Hackersh::

	"http://localhost" -> url -> nmap -> w3af

Or:

.. image:: http://hackersh.org/helloworld.png


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

Examples
--------

For more examples please take a look at the `examples <https://github.com/ikotler/hackersh/tree/master/examples>`_ directory

Documentation
-------------

Full documentation is available at http://docs.hackersh.org/.

Please Help Out
---------------

This project is still under development. Feedback and suggestions are very
welcome and I encourage you to use the `Issues list
<http://github.com/ikotler/hackersh/issues>`_ on GitHub to provide that
feedback.

Contributors are welcome. Please refer to the `development
<http://docs.hackersh.org/en/latest/development.html>`_ section in the
documentation for guidelines.

Any questions, tips, or general discussion can be posted to our Google group:
`http://groups.google.com/group/hackersh-dev <http://groups.google.com/group/hackersh-dev>`_

License
-------

Hackersh is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2, or (at your option) any later version.
