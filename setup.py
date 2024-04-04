#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = [line.strip() for line in f.readlines() if bool(line.strip())]

test_requirements = [
    "pytest>=3",
]

extras_require = {
    "analyser": [
        "networkx",
        "matplotlib",
    ]
}

setup(
    author="Duy Dao",
    python_requires=">=3.9",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
    ],
    description="Python streaming library.",
    install_requires=requirements,
    extras_require=extras_require,
    license="MIT license",
    include_package_data=True,
    keywords="pystream",
    name="pystream",
    packages=find_packages(include=["pystream"]),
    test_suite="tests",
    tests_require=test_requirements,
    version="0.1.0",
    zip_safe=False,
)
