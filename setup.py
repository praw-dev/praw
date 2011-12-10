try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='reddit',
    version='1.1.1',
    packages=['reddit'],
    package_data={'reddit': ['*.cfg']},
    author='mellort',
    author_email='timothy.mellor+pip@gmail.com',
    description='A Python wrapper for the Reddit API',
    url='https://github.com/mellort/reddit_api',
    keywords=['reddit']
)
