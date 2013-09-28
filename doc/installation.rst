.. _installation:

Installation
============

This part of the documentation covers the installation of Hackersh. The first
step to using any software package is getting it properly installed.


.. _installing:

-------------------
Installing Hackersh
-------------------

Hackersh requires Python version 2.6 and greater, but it will not work (yet)
with Python 3. Dependencies are listed in :file:`setup.py` and will be
installed automatically as part of any of the techniques listed below.

.. note::

  Hackersh will ***NOT*** install 3rd party security tools as part of its
  installation. You have to manually download and install each and every
  security tool that you wish to use in Hackersh. Alternatively, you can
  install Hackersh in a Linux distribution such as `BackTrack <http://www
  .backtrack-linux.org/>`_, `Kali <http://www.kali.org/>`_, or `Pentoo
  <http://www.pentoo.ch/>`_ and enjoy the already installed tools.


Distribute & Pip
----------------

Installing Hackersh is simple with `pip <http://www.pip-installer.org/>`_::

    $ pip install hackersh

or, with `easy_install <http://pypi.python.org/pypi/setuptools>`_::

    $ easy_install hackersh

.. note::

    Using easy_install is discouraged. Why? `Read here <http://www.pip-installer.org/en/latest/other-tools.html#pip-compared-to-easy-install>`_.

-------------------
Download the Source
-------------------

You can also install Hackersh from source. The latest release (|version|) is available from GitHub.

* tarball_
* zipball_

Once you have a copy of the source, unzip or untar the source package, cd to the new directory, and: ::

    $ python setup.py install

To download the full source history from Git, see :ref:`Source Control <scm>`.

.. _tarball: http://github.com/ikotler/hackersh/tarball/master
.. _zipball: http://github.com/ikotler/hackersh/zipball/master


.. _updates:

Staying Updated
---------------

The latest version of Hackersh will always be available here:

* PyPi: http://pypi.python.org/pypi/hackersh/
* GitHub: http://github.com/ikotler/hackersh/

When a new version is available, upgrading is simple. ::

	$ pip install hackersh --upgrade
