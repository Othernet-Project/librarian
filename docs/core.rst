Core modules
------------

Core modules may be function based as long as they do not depend on any global
state. Lower-level core modules are even encouraged to be function based, while
higher level core modules are mostly class based (because most of them
inevitably depend on multiple configuration options).

In case of class based core modules, the classes must have complete
constructors, to ease a bit on development, and require no deep understanding
about the inner-workings of the classes by their users.

The usage of the core archive module is a good example of the intended goal.
As the archive is responsible for storing / retrieving all the data about the
content that librarian manages, it was designed so that it's not tied to a
specific storage backend. A storage backend is required to subclass the
``BaseArchive`` class and implement all the pre-specified methods.
In order to access the archive, the ``Archive`` class must be instantiated with
a valid storage backend. It is possible to instantiate the storage backend
manually, and pass that to the constructor of ``Archive``::

    backend = CustomStorageBackend(arg1='val1', arg2='val2')
    archive = Archive(backend)

Or to call the ``Archive.setup`` factory method with the path to the storage
backend that is meant to be used::

    archive = Archive.setup('path.to.storage.CustomStorageBackend',
                            arg1='val1',
                            arg2='val2')

In the latter example, ``Archive`` will attempt to instantiate the chosen
backend by itself, passing all the positional and keyword arguments that it
received to the backend's constructor.

After instantiation, all the methods that are defined on the ``BaseArchive``
class are accessible through this archive object.

``BaseArchive`` depends on a couple of configuration parameters that are
expected to be passed as keyword arguments, and are mandatory. An exception
will be raised if they are omitted during instantiation. The parameters are:

- ``unpackdir`` - Path to folder where zipballs are symlinked while unpacking
- ``contentdir`` - Path to content folder(where archive zipballs are stored)
- ``spooldir`` - Path for temporary content storage
- ``meta_filename`` - Name of the file that contains content metadata

All methods of a storage backend should return native python objects, not
backend specified objects.
