"""praw setup.py"""

import re
from codecs import open
from os import path
from setuptools import setup


PACKAGE_NAME = 'praw'
HERE = path.abspath(path.dirname(__file__))
with open(path.join(HERE, 'README.rst'), encoding='utf-8') as fp:
    README = fp.read()
with open(path.join(HERE, PACKAGE_NAME, '__init__.py'),
          encoding='utf-8') as fp:
    VERSION = re.search("__version__ = '([^']+)'", fp.read()).group(1)

dependencies = ['decorator >=4.0.9, <4.1',
                'requests >=2.3.0',
                'six ==1.10',
                'update_checker >=0.12, <1.0']

try:
    from OpenSSL import __version__ as opensslversion
    opensslversion = [int(minor) if minor.isdigit() else minor
                      for minor in opensslversion.split('.')]
    if opensslversion < [0, 15]:  # versions less than 0.15 have a regression
        dependencies.append('pyopenssl >=0.15')
except ImportError:
    pass  # open ssl not installed

setup(name=PACKAGE_NAME,
      author='Timothy Mellor',
      author_email='timothy.mellor+pip@gmail.com',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: Implementation :: CPython',
          'Topic :: Utilities'],
      description=('PRAW, an acronym for `Python Reddit API Wrapper`, is a '
                   'python package that allows for simple access to '
                   'reddit\'s API.'),
      entry_points={'console_scripts': [
          'praw-multiprocess = praw.multiprocess:run']},
      install_requires=dependencies,
      keywords='reddit api wrapper',
      license='GPLv3',
      long_description=README,
      maintainer='Bryce Boe',
      maintainer_email='bbzbryce@gmail.com',
      package_data={'': ['COPYING'], PACKAGE_NAME: ['*.ini']},
      packages=[PACKAGE_NAME],
      tests_require=['betamax >=0.5.1, <0.6',
                     'betamax-matchers >=0.2.0, <0.3',
                     'betamax-serializers >=0.1.1, <0.2',
                     'mock ==1.0.1'],
      test_suite='tests',
      url='https://praw.readthedocs.io/',
      version=VERSION)
