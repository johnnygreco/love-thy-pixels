#!/usr/bin/env python 

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='ltpix',
      version='0.1',
      author='Johnny Greco',
      author_email='jgreco.astro@gmail.com',
      packages=['ltpix'],
      url='https://github.com/johnnygreco/love-thy-pixels')
