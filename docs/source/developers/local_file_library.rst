Local file library
==================

While developing Libarian features or external Librarian components, you
probably want to have some files to work with. If you've folled the
instructions in :doc:`download_and_setup`, you probably have a directory called
``tmp/library``, which is where the files should be stored.

.. note::
    If ``tmp/library`` directory does not exist, it will be created when
    starting FSAL. There is nothing wrong with manually creating it, though.

After adding new files and directories into the library, they need to be
reindexed by FSAL before they show up. Reindexing can be triggered either by
restarting FSAL, or by using the ``reindex`` make target.

To restart FSAL::

    $ make restart-fsal

To reindex without restarting FSAL::

    $ make reindex
