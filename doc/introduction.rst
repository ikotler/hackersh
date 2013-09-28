.. _introduction:

Introduction
============

Read this before you get started with Hackersh. This hopefully answers some
questions about the purpose and goals of the project, and when you should or
should not be using it.

Philosophy
----------

“The whole is greater than the sum of its parts.”
  ― Aristotle

What is Hackersh?
------------------

Hackersh ("Hacker Shell") is a free and open source command-line shell and
scripting language designed especially for security testing.

Just like Linux system administrators are using shell scripting to automate tasks: ::

	> /sbin/ifconfig | /bin/grep "inet addr:" | /usr/bin/cut -d: -f2 | /usr/bin/awk '{ print $1 }'
	127.0.0.1

Hackersh aims to help security testers to automate their tasks: ::

	> /sbin/ifconfig | /bin/grep "inet addr:" | /usr/bin/cut -d: -f2 | /usr/bin/awk '{ print $1 }' | ipv4_address | nmap | nikto

	Properties:
	-----------

	+--------------+-----------+
	| Property     | Value     |
	+--------------+-----------+
	| Ipv4_Address | 127.0.0.1 |
	+--------------+-----------+
	| Name         | 127.0.0.1 |
	+--------------+-----------+
	| Service      | HTTP      |
	+--------------+-----------+
	| Proto        | TCP       |
	+--------------+-----------+
	| Port         | 80        |
	+--------------+-----------+

	Graph:
	------

	127.0.0.1 <via str>
	`-127.0.0.1 <via ipv4_address>
	  `-80/tcp (HTTP) <via nmap_result_#1>
	    `-Found #4 Vulnerabilities <via nikto>

	Vulnerabilities:
	----------------

	+----------------------------------------------------------------------------------+-----------------------------------+
	| VULNERABILITY DESCRIPTION                                                        | URL                               |
	+----------------------------------------------------------------------------------+-----------------------------------+
	| ETag header found on server, inode: 436622, size: 177, mtime: 0x4e22ce6d50080    | http://localhost:80/              |
	+----------------------------------------------------------------------------------+-----------------------------------+
	| Allowed HTTP Methods: GET, HEAD, POST, OPTIONS                                   | http://localhost:80/              |
	+----------------------------------------------------------------------------------+-----------------------------------+
	| /server-status: This reveals Apache information. Comment out appropriate line in | http://localhost:80/server-status |
	| httpd.conf or restrict access to allowed hosts.                                  |                                   |
	+----------------------------------------------------------------------------------+-----------------------------------+
	| /icons/README: Apache default file found.                                        | http://localhost:80/icons/README  |
	+----------------------------------------------------------------------------------+-----------------------------------+

It is written in Python and uses Pythonect as its scripting engine.

Continue to :ref:`installation` or :ref:`quickstart`
