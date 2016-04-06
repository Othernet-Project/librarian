Appendix C: Installing dependencies editably
============================================

Editable install feature (setuptools, pip) allows us to install a dependency
package into a virtualenv (or in global site-packages) such that it links to a
local source code directory rather than being a separate copy. This allows us
to edit the code in the source code directory and see the changes reflected in
the site-packages while the package is still available just like a proper
install.

If you are working on a dependency or external components, and you want an
editable install, you may need to set these up manually. Here we will take a
look at an example for FSAL.

Supposing that a local git repository for FSAL is located one level above the
librarian source tree (``../fsal``), we can do this::

    $ pip install -e ../fsal

Then you need to edit the FSAL configuration file to match the new location.
The line that you need to edit is in the ``[config]`` section::

    [config]

    defaults = 
        /path/to/site-packages/fsal/fsal-server.ini

Edit the line just below ``defaults=`` so it points to the ``fsal-server.ini``
in the local git repository. The paths are resolved relative to the location of
the configuration file, so::

    [config]

    defaults = 
        ../../fsal/fsal-server.ini
