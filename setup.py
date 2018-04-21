# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import unicode_literals

import io
import os.path
import sys

import setuptools


REQUIREMENT_DIR = "requirements"
ENCODING = "utf8"


def need_pytest():
    return set(["pytest", "test", "ptr"]).intersection(sys.argv)


with io.open("README.rst", encoding=ENCODING) as fp:
    long_description = fp.read()

with io.open(os.path.join("docs", "pages", "introduction", "summary.txt"), encoding=ENCODING) as f:
    summary = f.read().strip()

with open(os.path.join(REQUIREMENT_DIR, "requirements.txt")) as f:
    install_requires = [line.strip() for line in f if line.strip()]

with open(os.path.join(REQUIREMENT_DIR, "test_requirements.txt")) as f:
    tests_require = [line.strip() for line in f if line.strip()]

setuptools.setup(
    name="pathvalidate",
    version="0.16.3",
    author="Tsuyoshi Hombashi",
    author_email="tsuyoshi.hombashi@gmail.com",
    url="https://github.com/thombashi/pathvalidate",
    keywords=[
        "path", "validation", "validator", "sanitize", "file",
        "Excel", "JavaScript", "LTSV", "SQLite",
    ],
    license="MIT License",
    description=summary,
    long_description=long_description,
    include_package_data=True,
    install_requires=install_requires,
    packages=setuptools.find_packages(exclude=["test*"]),
    setup_requires=["pytest-runner"] if need_pytest() else [],
    tests_require=tests_require,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ])
