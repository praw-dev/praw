from setuptools import setup, find_packages

setup(
    name = "reddit",
    version = "1.0",
    packages = find_packages(),
    install_requires = ['setuptools'],
    author = "mellort",
    description = "A Python wrapper for the Reddit API",
    url = "https://github.com/mellort/reddit_api"
)

