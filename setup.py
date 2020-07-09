from setuptools import find_packages, setup

import localfunk

setup(
    name=localfunk.__NAME__,
    version=localfunk.__VERSION__,
    author=localfunk.__AUTHOR__,
    author_email=localfunk.__AUTHOR_EMAIL__,
    description=localfunk.__DESCRIPTION__,
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    license=localfunk.__LICENSE__,
    url=localfunk.__HOMEPAGE__,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=["flask", "pyngrok", "cfn-flip"],
    entry_points={"console_scripts": ["localfunk=localfunk.main:main",]},
)
