import pathlib

from setuptools import setup

# TODO: Add auto discovery for packages.
setup(
    name="lbz",
    version=pathlib.Path("version").read_text("utf-8"),
    author="Piotr Dyba",
    author_email="piotr.dyba@localbini.com",
    packages=["lbz", "lbz.authz", "lbz.dev", "lbz.events", "lbz.lambdas"],
    package_data={"lbz": ["py.typed"]},
    scripts=[],
    url="https://github.com/pdyba/lambdalizator",
    license="LICENSE",
    description="AWS Lambda REST ToolBox",
    long_description_content_type="text/markdown",
    long_description=pathlib.Path("README.md").read_text("utf-8"),
    install_requires=[
        "boto3 >=1.21.0, <1.22.0",
        "multidict >=6.0.0, <6.1.0",
        "python-jose >=3.3.0, <3.4.0",
    ],
    classifiers=[
        "Environment :: Web Environment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
    ],
    python_requires=">=3.8",
)
