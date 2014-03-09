#!/usr/bin/env python
from __future__ import print_function

from distutils.core import setup


__author__ = "Alexander Weigl"
__date__ = "2014-03-08"
__version__ = "0.1"

desc = open("README.md").read()

setup(
    name='musiclib',
    version=__version__,
    description='',  #TODO
    author=__author__,
    url='http://student.kit.edu/~uiduw/',
    maintainer="Alexander Weigl",
    maintainer_email="Alexander.Weigl@student.kit.edu",
    packages=['musicbib'],
    platforms="linux",
    long_description=desc,

    keywords='',  #TODO
    license='gpl3',

    classifiers=[
        'Operating System :: POSIX',
        'Programming Language :: Python',
    ],
    zip_safe=True
)


