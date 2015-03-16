======================================
Setting up the development environment
======================================

The instructions for setting up the development environment is aimed at both
developers and non-developers. If you are a translator, or someone who is
simply interested in seeing Librarian in action, please follow these
instructions. If you still have questions, please visit our forums_ or file an
issue in our `issue tracker`_.

If you are an experienced Python developer, though, you probably don't need to
go through this. Skip to straight to `Running Librarian`_. The requirements
file is in the ``conf`` directory.

There are two ways to set up your development envioronment. You can either
create a local development environment (Python 2.7.x) or use Vagrant_ and
VirtualBox_.

Using Vagrant/Virtualbox
------------------------

Using a virtual machine is generally simpler as the script supplied with
Librarian's source code will perform all necessary setup. If you have both
Vagrant and Virtualbox installed, you can simply do::

    vagrant up

You can then SSH into the virtual machine using this command::

    vagrant ssh

Once inside, you can start Librarian by typing::

    sudo python -m librarian.app

Installing Python
-----------------

Under Windows or Mac, simply run the official installer.

On Ubuntu and Debian, you will need to install python3 package. Information
about availability of different versions of Python for your system is outside
the scope of this document. Simply run this command::

    sudo apt-get install python3

On Arch Linux, Python 3 package is called `python`, and you can install it with 
pacman::

    sudo pacman -S python

Installing build tools
----------------------

Librarian requires some binary dependencies to be compiled (namely, gevent,
and, on Unix and Linux, also bjoern). These dependencies rely on libev_ on Unix
and Linux.

You will need to have build tools installed. On Mac OSX, you may install XCode
and GNU compilers. On Linux, you need to find instructions for your
distribution. On Windows, install the `Visual C++ Compiler for Python 2.7`_.

On Unix and Linux systems, you will also need the headers for libev. In some
Linux distribution, the package may be called ``libev-dev` or ``libev-devel``.
You may also need to install Python source code if it is not included with the
Python distribution. The Python sources are usually found in packages that are
called ``python-dev`` or ``python-devel``. In any case, refer to your
distribution's documentation for more information.

Installing pip
--------------

Windows users may skip this section as pip is included with Windows
distributions of Python.

Pip is Python's package manager, which is used to install Python libraries
necessary to run Librarian. While you can install packages manually if you
want, it is recommended that you use pip if you're new to Python.

On all platforms, pip is installed using a simple ``get-pip.py`` script.
Download the script from here::

    https://bootstrap.pypa.io/get-pip.py

On Windows, open Windows Explorer, navigate to the location where you have
downloaded the file, and Shift-right-click on empty area in the file list, and
select the 'Open Command Window Here' context menu item. This opens the command
prompt window. On Linux and Mac, open the terminal and navigate your way to the
file (replace ``/path/to/file`` with the actual path of the file you've
downloaded)::

    cd /path/to/file

If you don't know where you file is located, you can usually find out by
right-clicking it and selecting the 'Properties' context menu item. Details on
how to get the file's path on different systems is outside the scope of this
document.

Next (for all operating systems), type::

    python get-pip.py

This should install pip on your system. On some Unix/Linux systems, you may
need to use ``sudo``::

    sudo python get-pip.py

Install virtualenv
------------------

If you plan to work on more than one Python project, it would be desirable to
install virtualenv and set up a vritual environment for Librarian. If you don't
want to bother with virtualenv or you don't think you'd be working with Python
projects other than Librarian, you may skip this section.

Although you can install the `virtualenv` package using pip, it's much easier
to use `virtualenvwrapper` that helps you create and delete environments.
Follow the `install instructions`_ for virtualenvwrapper and continue with this
documentation when you're done.

Create a virtual environment for Librarian by opening a terminal (Command
Propmpt on Windows) and typing the following command::

    mkvirtualenv librarian

The rest of the document will assume your virtual environment is named
``librarian``. If you wish to use another name, replace ``librarian`` in the
above command with whatever name you prefer. 

Obtaining the source code
-------------------------

You can obtain the source code in several ways:

- Clone GitHub repository
- Download zip file with sources from GitHub
- Install Librarian without sources (simple, but not for development)

Cloning the GitHub repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We assume that only developers will want to do this, so we won't go into
details on how to install Git and other toos you may want/need. Clone the
repository using this command::

    git clone https://github.com/Outernet-Project/librarian.git

Downloading the zip file with sources
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you do not have and do not want to install Git, you can download the source
code. Use this URL::

    https://github.com/Outernet-Project/librarian/archive/master.zip

The source code is contained in the zip file.

Installing without sources
~~~~~~~~~~~~~~~~~~~~~~~~~~

Librarian can be installed without the complete source code. This method is
only possible for officially released version of Librarian, and requires you to
have pip installed (see `Installing pip`_). 

If you chose to use virtualenv, make sure the virtual environment is active.
Type the following command::

    workon librarian

Now type the following command::

    pip install http://outernet-project.github.io/orx-install/librarian-0.1b1.zip

Installing required Python libraries
====================================

Librarian depends on a few Python libraries for correct operation, and they
need to be present before you can run Librarian. If you installed Librarian
without sources, you may skip this step.

On Windows, go to the folder where sources are cloned/unpacked,
Shift-right-click and select the 'Open Command Window Here' option. On other
systems, open a terminal and navigate to the source directory/folder.

If you created a virtualenv for Librarian, make sure it's active::

    workon librarian

Use the following command to install the libraries::

    # On Windows
    pip install -r conf\requirements.txt

    # On other platforms
    pip install -r conf/requirements.txt\

Preparation
===========

If you opted to use virtualenv, make sure it's activated. Simply type::

    workon librarian

Now set the development environment up::
    
    # On windows
    setup develop

    # On other platforms
    python setup.py develop

If this command fails, you migth be missing gettext_, so make sure it's
installed.

Running tests
=============

Before you run tests, you need to install development requirements. Make sure
your virtualenv is active and use the following command::

    # On Windows
    pip install -r conf\dev_requirements.txt

    # On other platforms
    pip install -r conf/dev_requirements.txt

Now you can run the tests with the following command::

    setup test

Test runner used by setup module is `py.test`_. You can pass any arguments to
it using the ``-a`` switch. For example, to test a single module::

    setup test -a path/to/module

.. note::

    Note that Windows uses should always use forward slashes when passing
    arguments using the ``-a`` switch.

Running Librarian
=================

To run Librarian, open your terminal, navigate to the directory (folder) where
the source code is located, and run the following command::

    python -m librarian.app --conf local.ini

This should start a development server running at `127.0.0.1:8080`_.

.. _forums: https://discuss.outernet.is/
.. _issue tracker: https://github.com/Outernet-Project/librarian/issues
.. _Python download page: https://www.python.org/downloads/
.. _instructions in Git book: http://git-scm.com/book/en/v2/Getting-Started-Installing-Git
.. _install instructions: http://virtualenvwrapper.readthedocs.org/en/latest/install.html
.. _127.0.0.1:8080: http://127.0.0.1:8080/
.. _gettext: https://www.gnu.org/software/gettext/
.. _py.test: http://pytest.org/latest/
.. _Visual C++ Compiler for Python 2.7: http://www.microsoft.com/en-us/download/details.aspx?id=44266
.. _Vagrant: https://www.vagrantup.com/
.. _VirtualBox: https://www.virtualbox.org/
.. _libev: http://freecode.com/projects/libev
