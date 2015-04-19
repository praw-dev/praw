import os
import re
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

PACKAGE_NAME = 'praw'


HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(HERE, 'README.rst')) as fp:
    README = fp.read()
with open(os.path.join(HERE, PACKAGE_NAME, '__init__.py')) as fp:
    VERSION = re.search("__version__ = '([^']+)'", fp.read()).group(1)


setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author='Timothy Mellor',
    author_email='timothy.mellor+pip@gmail.com',
    maintainer='Bryce Boe',
    maintainer_email='bbzbryce@gmail.com',
    url='https://praw.readthedocs.org/',
    description=('PRAW, an acronym for `Python Reddit API Wrapper`, is a '
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
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.1',
                 'Programming Language :: Python :: 3.2',
                 'Programming Language :: Python :: 3.3',
                 'Programming Language :: Python :: 3.4',
                 'Topic :: Utilities'],
    license='GPLv3',
    keywords='reddit api wrapper',
    packages=[PACKAGE_NAME],
    package_data={'': ['COPYING'], PACKAGE_NAME: ['*.ini']},
    install_requires=['requests>=2.3.0', 'six>=1.4', 'update_checker>=0.11'],
    tests_require=['betamax>=0.4.2', 'betamax-matchers>=0.1.0', 'mock>=1.0.0'],
    entry_points={'console_scripts': [
            'praw-multiprocess = praw.multiprocess:run']},
    test_suite='tests')
