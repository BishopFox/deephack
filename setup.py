#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name='deephack',
    version='1.0.0',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'uwsgi',
        'coverage',
        'Flask',
        'psycopg2',
        'sqlalchemy',
        'scipy',
        'numpy',
        'keras',
        'ipython',
        'faker',
    ],
    classifiers=[
        'Private :: Do Not Upload'
    ],
    entry_points={
        'console_scripts': [
            'vulnserver = vulnserver.cli.vulnserver:main',
        ]
    }
)
