# See docs/license.rst for license details.
# Copyright (c) 2017-2020 Chris Withers

import os

from setuptools import setup, find_packages

base_dir = os.path.dirname(__file__)

setup(
    name='sybil',
    version='2.0.0',
    author='Chris Withers',
    author_email='chris@withers.org',
    license='MIT',
    description="Automated testing for the examples in your documentation.",
    long_description=open('README.rst').read(),
    url='https://github.com/cjw296/sybil',
    classifiers=[
        # 'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(exclude=['tests', 'functional_tests']),
    zip_safe=False,
    include_package_data=True,
    extras_require=dict(
        test=[
            'pytest>=3.5.0',
            'pytest-cov',
            ],
        build=['sphinx', 'setuptools-git', 'twine', 'wheel']
    ),
)
