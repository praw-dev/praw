"""praw setup.py"""

import re
from codecs import open
from os import path
from setuptools import find_packages, setup


PACKAGE_NAME = 'praw'
HERE = path.abspath(path.dirname(__file__))
with open(path.join(HERE, 'README.rst'), encoding='utf-8') as fp:
    README = fp.read()
with open(path.join(HERE, PACKAGE_NAME, 'const.py'),
          encoding='utf-8') as fp:
    VERSION = re.search("__version__ = '([^']+)'", fp.read()).group(1)


setup(name=PACKAGE_NAME,
      author='Bryce Boe',
      author_email='bbzbryce@gmail.com',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
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
      install_requires=['decorator >=4.0.9, <4.1',
                        'prawcore >=0.5.0, <0.6',
                        'requests >=2.3.0',
                        'six ==1.10',
                        'update_checker >=0.12'],
      keywords='reddit api wrapper',
      license='Simplified BSD License',
      long_description=README,
      package_data={'': ['LICENSE.txt'], PACKAGE_NAME: ['*.ini']},
      packages=find_packages(exclude=['tests', 'tests.*']),
      setup_requires=['pytest-runner ==2.7'],
      tests_require=['betamax >=0.8, <0.9',
                     'betamax-matchers >=0.2.0, <0.3',
                     'betamax-serializers >=0.2, <0.3',
                     'mock ==1.0.1',
                     'pytest ==2.8.7'],
      test_suite='tests',
      url='https://praw.readthedocs.org/',
      version=VERSION)
