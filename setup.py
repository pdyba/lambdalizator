from setuptools import setup
import pathlib

setup(
    name="lbz",
    version=pathlib.Path("version").read_text("utf-8"),
    author="Piotr Dyba",
    author_email="piotr.dyba@localbini.com",
    packages=["lbz", "lbz.dev", "lbz.authz"],
    package_data={"lbz": ["py.typed"]},
    scripts=[],
    url="https://github.com/pdyba/lambdalizator",
    license="LICENSE",
    description="AWS Lambda REST ToolBox",
    long_description_content_type="text/markdown",
    long_description=pathlib.Path("README.md").read_text("utf-8"),
    install_requires=["python-jose"],
    classifiers=[
        "Environment :: Web Environment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
    ],
    python_requires=">=3.8",
)
