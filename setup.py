import os, re
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

PACKAGE_NAME = 'praw'

HERE = os.path.abspath(os.path.dirname(__file__))
INIT = open(os.path.join(HERE, PACKAGE_NAME, '__init__.py')).read()
README = open(os.path.join(HERE, 'README.md')).read()

VERSION = re.search("__version__ = '([^']+)'", INIT).group(1)


setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author='Timothy Mellor',
    author_email='timothy.mellor+pip@gmail.com',
    maintainer='Bryce Boe',
    maintainer_email='bbzbryce@gmail.com',
    url='http://python-reddit-api-wrapper.readthedocs.org/',
    description=('PRAW, an acronym for "Python Reddit API Wrapper", is a '
                 'python package that allows for simple access to '
                 'reddit\'s API.'),
    long_description=README,
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Environment :: Console',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'Natural Language :: English',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 2.6',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3.2',
                 'Topic :: Utilities'],
    license='GPLv3',
    keywords='reddit api wrapper',
    packages=[PACKAGE_NAME],
    package_data={'': ['COPYING'], PACKAGE_NAME: ['*.ini']},
    install_requires=['six'],
    test_suite='praw',
    )
