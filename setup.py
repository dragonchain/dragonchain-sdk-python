#!/usr/bin/env python3

import os
import re
import sys

import setuptools


def get_version():
    root = os.path.dirname(os.path.abspath(__file__))
    init = open(os.path.join(root, "dragonchain_sdk", "__init__.py")).read()
    return re.compile(r"""__version__ = ['"]([0-9.]+.*)['"]""").search(init).group(1)


CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 4)

if CURRENT_PYTHON < REQUIRED_PYTHON:
    sys.stderr.write(
        """
==========================
Unsupported Python version
==========================
This version of dragonchain-sdk requires Python {}.{}, but you're
trying to install it on Python {}.{}.
This may be because you are using a version of pip that doesn't
understand the python_requires classifier. Make sure you
have pip >= 9.0 and setuptools >= 24.2, then try again:
    $ python -m pip install --upgrade pip setuptools
""".format(
            *(REQUIRED_PYTHON + CURRENT_PYTHON)
        )
    )
    sys.exit(1)


setuptools.setup(
    name="dragonchain_sdk",
    version=get_version(),
    python_requires=">={}.{}".format(*REQUIRED_PYTHON),
    author="Dragonchain",
    author_email="support@dragonchain.com",
    description="Dragonchain SDK for Python",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    url="https://dragonchain.com",
    packages=setuptools.find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_data={"dragonchain_sdk": ["py.typed"]},
    include_package_data=True,
    zip_safe=False,
    scripts=[],
    install_requires=["requests>=2.4.0", 'typing;python_version<"3.5"'],
    extras_require={"aio": ["aiohttp>=3.5.0"]},
    license="Apache License 2.0",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Typing :: Typed",
    ],
    project_urls={
        "Documentation": "https://python-sdk-docs.dragonchain.com/latest/",
        "Source": "https://github.com/dragonchain/dragonchain-sdk-python",
        "Bug Tracker": "https://github.com/dragonchain/dragonchain-sdk-python/issues",
    },
)
