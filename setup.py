import pathlib

from setuptools import find_packages, setup

setup(
    name="lbz",
    version=pathlib.Path("version").read_text("utf-8").strip(),
    author="Piotr Dyba",
    author_email="piotr.dyba@localbini.com",
    packages=find_packages(exclude=["examples", "examples.*", "tests", "tests.*"]),
    package_data={"lbz": ["py.typed"]},
    scripts=[],
    url="https://github.com/pdyba/lambdalizator",
    license="LICENSE",
    description="AWS Lambda REST ToolBox",
    long_description_content_type="text/markdown",
    long_description=pathlib.Path("README.md").read_text("utf-8"),
    install_requires=[
        "boto3>=1.40.0,<1.41.0",
        "multidict>=6.6.0,<6.7.0",
        "python-jose>=3.5.0,<3.6.0",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
)
