.. _development:

Development
===========

Hackersh is under active development, and contributors are welcome.

If you have a feature request, suggestion, or bug report, please open a new
issue on `GitHub <http://github.com/ikotler/hackersh>`_.

-----------------------------
Contributor License Agreement
-----------------------------

Before we can accept code, patches or pull requests on `GitHub <http://github.com/ikotler/hackersh>`_, there's a
quick web form we need you to fill out `here <http://www.clahub.com/agreements/ikotler/hackersh>`_ (**scroll to the
bottom!**).

Hackersh’s CLA is a copy of the one used by Sun Microsystems for all
contributions to their projects.

This particular agreement has been used by other software projects in addition
to Sun and is generally accepted as reasonable within the Open Source
community.

`More about CLAs <https://www.google.com/search?q=Contributor%20License%20Agreement>`_


.. _scm:

--------------
Source Control
--------------

Hackersh source is controlled with Git_, the lean, mean, distributed source control machine.

The repository is publicly accessable.

    ``git clone git://github.com/ikotler/hackersh.git``

The project is hosted on `GitHub <http://github.com/ikotler/hackersh>`_.


Git Branch Structure
++++++++++++++++++++

Feature / Hotfix / Release branches follow a `Successful Git Branching Model`_. Git-flow_ is a great tool for managing the repository. I highly recommend it.

``develop``
    The "next release" branch. Likely unstable.
``master``
    Current production release (|version|) on PyPi.

Each release is tagged.

When submitting patches, please place your feature/change in its own branch prior to opening a pull reqeust on `GitHub <http://github.com/ikotler/hackersh>`_.


.. _Git: http://git-scm.org
.. _`Successful Git Branching Model`: http://nvie.com/posts/a-successful-git-branching-model/
.. _git-flow: http://github.com/nvie/gitflow


.. _newcomponents:

---------------------
Adding New Components
---------------------

TBD

.. _docs:

-----------------
Building the Docs
-----------------

Documentation is written in the powerful, flexible, and standard Python documentation format, `reStructured Text`_.
Documentation builds are powered by the powerful Pocoo project, Sphinx_. The :ref:`API Documentation <api>` is mostly documented inline throughout the module.

The Docs live in ``hackersh/doc``. In order to build them, you will first need to install Sphinx: ::

    $ pip install sphinx


Then, to build an HTML version of the docs, simply run the following from the **doc** directory: ::

    $ make html

Your ``doc/_build/html`` directory will then contain an HTML representation of the documentation, ready for publication on most web servers.

You can also generate the documentation in **epub**, **latex**, and **json**.


.. _`reStructured Text`: http://docutils.sourceforge.net/rst.html
.. _Sphinx: http://sphinx.pocoo.org
