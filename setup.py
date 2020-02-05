#!/usr/bin/env python

from setuptools import setup, find_packages

__VERSION__ = "1.0.7"

with open("requirements.txt", encoding="utf-8") as f:
    requirements = f.read().splitlines()

with open("README.md", "r", encoding="utf-8") as fh:
    readme = fh.read()

setup(
    name="stjudecloud-oliver",
    version=__VERSION__,
    description="An opinionated Cromwell orchestration system",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="St. Jude Cloud Team",
    author_email="support@stjude.cloud",
    scripts=["scripts/oliver"],
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.0, <3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
)
