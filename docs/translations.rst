====================
Testing translations
====================

This document outlines the procedure for testing translation files. It's
assumed that you have completed the steps in the Development environment
documentation. If not, please follow the steps in the ``docs/dev_env.rst``
document before continuing. Make sure you know how to activate the virtualenv
(if you are using it), and you know how to run Librarian. 

For some of the operations discussed below, you may need to use a text editor
and modify the sources. If you are not familiar with editing source code, we
suggest you install SublimeText_ (free with nag screen). On Windows, do not use 
Notepad.

We assume you will be doing your translation work on POEditor_. You can `join
the project`_ if you haven't already.

Requirements
============

To test translation files, you need to have gettext installed. On most Linux
systems, you should be able to install a ``gettext`` package. 

Windwos users can download the `setup program`_ and run it. Make sure that
gettext commands are available in the Command Prompt after installation. Open
Command Prompt and type::

    xgettext --help

If the system complains it cannot find the command, you will need to add the
gettext install location to system PATH environment variable. Follow this
tutorial_. The usual install location on Windows is::

    C:\Program Files (x86)\gettext-utils

Testing translation files
=========================

To test the translation files, you first need to download the translation you
are working on in ``.po`` format (this is usually the default when you click
the download link in POEditor). Got to the language you are working on, and
click the download icon on the right.

Once your .po file is downloaded, rename it to ``librarian.po`` and overwrite
the one found in ``librarian/locales/??/LC_MESSAGES`` directory/folder. The
``??`` stands for language code for your language. If you're unsure, don't
hesitate to ask by posting a comment on POEditor or in our forums_. You can
open ``librarian/app.py`` in your editor. You will find the code-name mapping
for all supported languages around line 50. The following is a list of those
mappings (it may not always be up to date, though)::

    ar - اللغة العربية
    da - Dansk
    de - Deutsch
    en - English
    es - Español
    fr - Français
    jp - 日本語
    nb - Norsk
    pt - Português
    sr - Srpski
    sv - Svensk
    ta - தமிழ்
    tr - Türkçe
    zh - 中文

If you cannot find a directory that matches the language you are working on,
see the next section first.

Once your file is copied, you need to compile the message catalogs. 

On Windows, open Explorer, and navigate to the folder where the source code is
located. Shift-right-click and select the 'Start Command Window Here' option.
Make sure the virtualenv is active (if you use it) and type::

    python scripts/cmpmsgs.py librarian

When it says 'Done', you can start the development server and test the
translation.

If you run into any issues while testing translations (e.g., error page, errors
during compiling, etc), please post the details in our forums_.

Adding languages that do not appear in the langauge bar
=======================================================

If the language you are working on does not appear in librarian's langauge bar,
it is not supported yet (probably because the translation wasn't complete). You
will need to edit the ``librarian/app.py`` file and add it manually.

Find a line that says ``LOCALES = (``. Languages are listed below that line in
the following format::

    ('lc', 'Language name'),

``'lc'`` (with single quotes) is the language code. If you don't know what
langauge code is used by your language, see `this page`_ Look under the ISO
639-1 column. If you are still not sure, post in our forums_. The ``'Language
name'`` (with single quotes) should be the name of the language in the language
you are adding. For example, Japanese is '日本語'.

Next create a directory in ``librarian/locales`` that is named after the
language code. For instance, for 'jp' locale, it would be
``librarian/locales/jp``. Inside it, create a directory named ``LC_MESSAGES``.
You end up with ``librarian/locales/jp/LC_MESSAGES``. You may now continue with
the procedure described in the previous section and compile the translation
files.

Extracting messages
===================

You generally don't need to extract messages if you're not fixing the original
(source) strings in the Librarian source code. This section is provided for
people who wish to work on Librarian sources and/or proof-read the source
strings.

If you are using virtualenv, make sure the environment is active. Run the
following command in the source directory::

    python scripts/xmsgs.py librarian -d librarian -a translations@outernet.is -m app


.. _setup program: http://sourceforge.net/projects/gnuwin32/files/gettext/0.14.4/gettext-0.14.4.exe/download?use_mirror=netcologne&download=
.. _POEditor: https://poeditor.com/projects/view?id=21376
.. _join the project: https://poeditor.com/join/project?hash=90911b6fc31f2d68c7debd999aa078c6
.. _tutorial: http://www.computerhope.com/issues/ch000549.htm
.. _SublimeText: http://www.sublimetext.com/
.. _forums: https://discuss.outernet.is/category/volunteering-for-outernet/translation
.. _this page: http://www.loc.gov/standards/iso639-2/php/code_list.php
