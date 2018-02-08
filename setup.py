#!/usr/bin/env python
# -*- coding:iso-8859-1
from __future__ import print_function
import sys

if sys.version[0:3] < '2.7':
    error = """\
ERROR: 'StoSim requires Python version 2.7 or above.'
Exiting."""
    sys.stderr.write(error)
    sys.exit(1)


from setuptools import setup
from setuptools.command.test import test as TestCommand
import codecs
import os
import re


here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    # intentionally *not* adding an encoding option to open
    return codecs.open(os.path.join(here, *parts), 'r').read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

long_description = read('README.rst')


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


setup(
    name='stosim',
    version=find_version('stosim', '__init__.py'),
    url='http://homepages.cwi.nl/~nicolas/stosim/',
    license='Apache Software License',
    author='Nicolas Höning',
    install_requires=['fjd==0.1.58'],
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    author_email='iam@nicolashoening.de',
    description='Stochastic Simulations',
    long_description=long_description,
    packages=['stosim', 'stosim.sim', 'stosim.analysis'],
    include_package_data=True,
    platforms='Unix',
    test_suite='stosim.tests.test_integration',
    classifiers = [
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Distributed Computing',
        'Topic :: Utilities',
        ],
    scripts = ['stosim/stosim']
)

