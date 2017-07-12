#!/usr/bin/env python
import setuptools


setuptools.setup(
    name="fmtlatex",
    url="https://github.com/goerz/fmtlatex",
    author="Michael Goerz",
    author_email="mail@michaelgoerz.net",
    description="Format LaTeX source code",
    install_requires=[
        'Click',
    ],
    extras_require={'dev': ['pytest',]},
    py_modules=['fmtlatex'],
    entry_points='''
        [console_scripts]
        fmtlatex=fmtlatex:main
    ''',
    classifiers=[
        'Environment :: Console',
        'Natural Language :: English',
        'License :: Public Domain',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
