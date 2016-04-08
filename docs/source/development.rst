***********************
Developer documentation
***********************

This chapter is dedicated to developers wishing to hack on Librarian internals
or create Librarian components.

If you wish to work on Libraian itself, you will need to know the following:

- Linux
- `Python <https://www.python.org/>`_
- `HTML <https://developer.mozilla.org/en-US/docs/Web/HTML>`_
- `SASS <http://sass-lang.com/>`_ (specifically the SCSS variant)
- `Compass <http://compass-style.org/>`_
- `CoffeeScript <http://coffeescript.org/>`_
- `PostgreSQL <http://www.postgresql.org/docs/9.5/interactive/index.html>`_
  (specifically the SQL syntax it uses)
- `GNU make and Makefiles <http://www.gnu.org/software/make/manual/make.html>`_
- `git <https://git-scm.com/>`_
- `non-blocking i/o <https://en.wikipedia.org/wiki/Asynchronous_I/O>`_

There could possibly be other topics not covered here, but becoming
familiarized with at least a majority of the topics listed should be good
enough to get started.

At very least, we will assume that you are reasonably familiar with how Python
development is done, that you can set up a virtualenv, and that you know how to
install packages using pip. We will also assume that you know how to set up a
PostgreSQL server and access it from Python.

This chapter will be divided into several chapters, mostly following the steps
one would normally take when approaching the Librarian code base for the first
time.

Topics covered:

.. toctree::
    :maxdepth: 1

    download_and_setup
    local_file_library
    source_code_layout
    architecture_overview
    core_api
    working_with_fsal
    database_access
    static_assets
    external_librarian_components
    components_exports
