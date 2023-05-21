#!/usr/bin/env python

import setuptools

with open("README.md", "r") as file:
    long_description = file.read()

setuptools.setup(
    name="fracability",
    version="0.1",
    description="",
    author="Gabriele Benedetti",
    author_email="",
    license="",
    url="",
    project_urls={
        'Documentation': '',
        'Source Code': 'https://github.com/gbene/FracAbility',
        'Donate': ''
    },
    keywords=[
        "reliability",
        "structural",
        "geology",
        "weibull",
        "lognormal",
        "exponential",
        "beta",
        "gamma",
        "normal",
        "loglogistic",
        "gumbel",
        "extreme",
        "value",
        "kaplan meier",
        "kaplan-meier",
        "survival",
        "analysis",
        "censored",
        "data",
        "lifelines",
        "probability",
        "distribution",
        "distributions",
        "fit",
        "fitting",
        "curve",
        "quality",
        "length",
        "fractures",
        "MCF",
        "mean",
        "cumulative",
        "CIF",
        "DS",
        "ZI",
        "defective",
        "subpopulation",
        "zero",
        "inflated",
        "DSZI",
        "likelihood",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Intended Audience :: Science/Research",
        "Topic :: Other/Nonlisted Topic",
        "Programming Language :: Python :: 3",
    ],
    install_requires=[
    ],
    python_requires=">=3.8",
    packages=setuptools.find_packages(
        exclude=["*.tests", "*.tests.*"]
    ),
)
