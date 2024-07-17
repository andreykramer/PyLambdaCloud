#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="pylambdacloud",
    version="1.0",
    description="Basic interface for launching tasks on Lambda Cloud instances using python.",
    author="Andrey Kramer",
    packages=find_packages(),
    install_requires=["requests", "inquirer", "fabric"],
    tests_require=["pytest"],
)
