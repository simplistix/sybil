# See docs/license.rst for license details.
# Copyright (c) 2017 onwards Chris Withers

import os

from setuptools import setup, find_packages

base_dir = os.path.dirname(__file__)

setup(
    name='sybil',
    version='4.0.1',
    author='Chris Withers',
    author_email='chris@withers.org',
    license='MIT',
    description="Automated testing for the examples in your code and documentation.",
    long_description=open('README.rst').read(),
    url='https://github.com/simplistix/sybil',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    packages=find_packages(exclude=['tests', 'functional_tests']),
    python_requires=">=3.7",
    extras_require=dict(
        test=[
            'myst_parser',
            'pytest>=7.1.0',
            'pytest-cov',
            'seedir',
            'testfixtures',
            ],
        build=['furo', 'sphinx', 'twine', 'wheel']
    ),
)
