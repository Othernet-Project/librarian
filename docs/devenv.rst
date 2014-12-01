======================================
Setting up the development environment
======================================

Due to some of the technical changes, Librarian *after* version 0.1b1 is not
able to run on Windows nor under Python 3.4. Because of this, recommended
method of running Librarian is using virtual environments with Linux.

Because of the above restrictions, we are now providing a ``Vagrantfile`` for
use with Vagrant_. Because of this, setting up a development environment has
become somewhat easier, but running Librarian on your computer now requires you
to install VirtualBox_ and Vagrant.

Once required software is installed, start the command prompt or terminal
emulator, navigate to the directory where Librarian code is located, and use
the following command to start the virtual machine::

    vagrant up

To enter the virtual machine, type::

    vagrant ssh

If you have questions regarding this document, please visit our forums_ or file
an issue in our `issue tracker`_.

Installing dependencies
=======================

From time to time (actually, whenever the contents of ``conf/requirements.txt`` 
file changes), you need to reinstall any dependencies. To do this, enter the
virtual machine and type::

    sudo pip install -r /vagrant/conf/requirements.txt

Running Librarian
=================

To start Librarian, enter the vritual machine and type::

    python /vagrant/run.py

This should start a development server running at `0.0.0.0:8080`_.

Troubleshooting
===============

Here are some common issues when running Librarian in the virtual environment:

No translations found
---------------------

If you receive an error that looks like this::

    IOError: [Errno 2] No translation file found for domain: u'librarian'

it means that compiled translation files are not found. This is normal.
Compiled translations are *not* shipped with the source code. You can compile
the translations using the ``scripts/cmpmsgs.py`` script. Before you can run
it, make sure that `GNU Gettext`_ is installed on your computer, as well as
Python interpreter (versions 2.7 and above should work).

Run the script like so::

    python scripts/cmpmsgs.py librarian/locales

If this has not resolved your issue, please check the output and make sure
there are no obvious errors that you can fix, then file a bug report in the
`issue tracker`_.

.. _Vagrant: https://www.vagrantup.com/
.. _VirtualBox: https://www.virtualbox.org/
.. _forums: https://discuss.outernet.is/
.. _issue tracker: https://github.com/Outernet-Project/librarian/issues
.. _`0.0.0.0:8080`: http://0.0.0.0:8080
.. _GNU Gettext: https://www.gnu.org/software/gettext/
