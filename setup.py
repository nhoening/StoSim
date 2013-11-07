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

setup(
    name='stosim',
    version=find_version('stosim', '__init__.py'),
    url='http://homepages.cwi.nl/~nicolas/stosim/',
    license='Apache Software License',
    author='Nicolas Höning',
    tests_require=[],
    install_requires=['fjd'],
    author_email='iam@nicolashoening.de',
    description='Stochastic Simulations',
    long_description=long_description,
    packages=['stosim'],
    include_package_data=True,
    platforms='Unix',
    classifiers = [
        'Programming Language :: Python',
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
