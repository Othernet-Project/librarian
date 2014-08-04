import os
from glob import glob
from setuptools import setup, find_packages


def read(fname):
    """ Return content of specified file """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def data(pattern):
    """ Returns normalized paths for given glob pattern """
    return [os.path.normpath(p) for p in glob(pattern)]

setup(
    name = 'librarian',
    version = '0.1a4',
    author = 'Outernet Inc',
    author_email = 'branko@outernet.is',
    description = ('Web-based UI for managing local Outernet broadcast '
                   'content'),
    license = 'GPLv3',
    keywords = 'outernet content archive library',
    url = 'https://github.com/Outernet-Project/librarian',
    packages=find_packages(),
    data_files=[
        ('', data('static/css/*.css')),
        ('', data('static/img/*.png')),
        ('', data('locales/**/LC_MESSAGES/*.[mp]o')),
        ('', data('migrations/*.sql')),
        ('', data('keys/*')),
        ('', data('librarian/views/*.tpl'))
    ],
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
