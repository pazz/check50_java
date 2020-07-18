#!/usr/bin/env python3

import setuptools
import glob
import os.path

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="check50_java",
    version="0.0.1",
    author="Patrick Totzke",
    author_email="patricktotzke@gmail.com",
    description="A check50 extension for java",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'check50',
    ],
    #zip_safe=False,
    package_data={'check50_java': ['lib/*.jar']},
)
