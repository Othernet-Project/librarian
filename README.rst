=========
librarian
=========

Librarian is an archive manager for Outernet Receiver. 

It reads the content of a directory where the content has been downloaded from 
the satellite receiver, and allows the user to sort, remove, and accept new
content into the Outernet Receiver's content archive. It also provides an
interface for browsing the archive. Finally, it provides mechanisms for
self-updating.

The current version does not provide any search capability. That feature is
planned for future releases.

We chose to use Arch Linux as development.

Development environment
=======================

To ensure uniform development environment, we are using Vagrant_. In
particular, we are using a `custom Vagrant base box`_ created for VirtualBox_ using
Arch Linux 32-bit version. The software will eventually run on ARMv6, but this
is not relevant for the software as it should be completely cross-platform.

Install Vagrant on your development computer. Then, get the Arch box by running
the following command::

    vagrant box add archlinux-i686 https://dl.dropboxusercontent.com/s/09iq7rmvs268t64/archlinux-i686-20140630.box

Use the i686 version of the base box later than v20140701.

It's important to name the box `archlinux-i686` as that is the name used in
the Vagrantfile. If you wnat to use a different name, you'll need to change it 
in the Vagrantfile as well, but don't commit the changes.

To create the new box using the supplied Vagrantfile, open the terminal, change
the directory to the source code directory, and run::

    vagrant up

Testing the app
===============

TODO


.. _Vagrant: http://www.vagrantup.com/
.. _custom Vagrant base box: https://github.com/Outernet-Project/archlinux-vagrant
.. _VritualBox: https://www.virtualbox.org/
