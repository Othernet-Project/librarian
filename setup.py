import os
from glob import glob
from setuptools import setup, find_packages

import librarian

def read(fname):
    """ Return content of specified file """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def data(patterns=[]):
    """ For each pattern, return mapping for data_files """
    data_files = []
    for pattern in patterns:
        pattern = os.path.join('librarian', pattern)
        paths = [os.path.normpath(p) for p in glob(pattern)]
        for p in paths:
            p = os.sep.join(p.split(os.sep)[1:])
            data_files.append(p)
    return data_files

setup(
    name = 'librarian',
    version = librarian.__version__,
    author = 'Outernet Inc',
    author_email = 'branko@outernet.is',
    description = ('Web-based UI for managing local Outernet broadcast '
                   'content'),
    license = 'GPLv3',
    keywords = 'outernet content archive library',
    url = 'https://github.com/Outernet-Project/librarian',
    packages=find_packages(),
    package_data={
        'librarian': data([
            'static/css/*.css',
            'static/img/*.png',
            'migrations/*.sql',
            'keys/*',
            'views/*.tpl',
            'locales/**/LC_MESSAGES/*.[mp]o',
            'librarian.ini',
        ]),
    },
    long_description=read('README.rst'),
    install_requires = [
        'bottle==0.12.7',
        'werkzeug==0.9.6',
        'CherryPy==3.3.0',
        'python-gnupg==0.3.6',
        'python-dateutil==2.2',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'Framework :: Bottle',
        'Environment :: Web Environment',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
