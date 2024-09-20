# See docs/license.rst for license details.
# Copyright (c) 2017 onwards Chris Withers

import os

from setuptools import setup, find_packages

base_dir = os.path.dirname(__file__)

PYTEST_VERSION_SPEC = 'pytest>=8'

setup(
    name='sybil',
    version='8.0.0',
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
    package_data={"sybil": ["py.typed"]},
    python_requires=">=3.9",
    extras_require=dict(
        pytest=[PYTEST_VERSION_SPEC],
        test=[
            'mypy',
            'myst_parser',
            PYTEST_VERSION_SPEC,
            'pytest-cov',
            'seedir',
            'testfixtures',
            'types-PyYAML',
            ],
        build=[
            'furo',
            'sphinx',
            'twine',
            'urllib3<2',  # workaround for RTD builds failing with old SSL
            'wheel',
        ]
    ),
)
