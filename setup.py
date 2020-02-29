#!/usr/bin/env python

import os
import re

from setuptools import setup, find_packages

root_dir = os.path.abspath(os.path.dirname(__file__))

with open(
    os.path.join(root_dir, "oliver", "__init__.py"), mode="r", encoding="utf-8"
) as fd:
    version = re.search(
        r"^__version__\s*=\s*[\"']([^\"']*)[\"']", fd.read(), re.MULTILINE
    ).group(1)

with open("requirements.txt", mode="r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

with open("README.md", mode="r", encoding="utf-8") as fh:
    readme = fh.read()

setup(
    name="stjudecloud-oliver",
    version=version,
    description="An opinionated Cromwell orchestration system",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="St. Jude Cloud Team",
    author_email="support@stjude.cloud",
    scripts=["bin/oliver"],
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
    python_requires=">=3.0, <3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
)
