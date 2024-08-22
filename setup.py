"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import os.path
from typing import Dict, Type

import setuptools


MODULE_NAME = "pathvalidate"
REPOSITORY_URL = f"https://github.com/thombashi/{MODULE_NAME:s}"
REQUIREMENT_DIR = "requirements"
ENCODING = "utf8"

pkg_info: Dict[str, str] = {}


def get_release_command_class() -> Dict[str, Type[setuptools.Command]]:
    try:
        from releasecmd import ReleaseCommand
    except ImportError:
        return {}

    return {"release": ReleaseCommand}


with open(os.path.join(MODULE_NAME, "__version__.py")) as f:
    exec(f.read(), pkg_info)

with open("README.rst", encoding=ENCODING) as fp:
    long_description = fp.read()

with open(os.path.join("docs", "pages", "introduction", "summary.txt"), encoding=ENCODING) as f:
    summary = f.read().strip()

with open(os.path.join(REQUIREMENT_DIR, "test_requirements.txt")) as f:
    TESTS_REQUIRES = [line.strip() for line in f if line.strip()]

with open(os.path.join(REQUIREMENT_DIR, "docs_requirements.txt")) as f:
    docs_requires = [line.strip() for line in f if line.strip()]

setuptools.setup(
    name=MODULE_NAME,
    url=REPOSITORY_URL,
    author=pkg_info["__author__"],
    author_email=pkg_info["__email__"],
    description=summary,
    keywords=["file", "path", "validation", "validator", "sanitization", "sanitizer"],
    license=pkg_info["__license__"],
    long_description=long_description,
    long_description_content_type="text/x-rst",
    include_package_data=True,
    packages=setuptools.find_packages(exclude=["test*"]),
    package_data={MODULE_NAME: ["py.typed"]},
    project_urls={
        "Changelog": f"{REPOSITORY_URL:s}/blob/master/CHANGELOG.md",
        "Documentation": f"https://{MODULE_NAME:s}.rtfd.io/",
        "Source": REPOSITORY_URL,
        "Tracker": f"{REPOSITORY_URL:s}/issues",
    },
    python_requires=">=3.7",
    extras_require={
        "docs": docs_requires,
        "readme": [
            "readmemaker>=1.1.0",
            "path>=13,<17",
        ],
        "test": TESTS_REQUIRES,
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Filesystems",
        "Topic :: Text Processing",
        "Typing :: Typed",
    ],
    zip_safe=False,
    cmdclass=get_release_command_class(),
)
