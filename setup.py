from setuptools import setup

with open("version") as file:
    version = file.read()

setup(
    name="lbz",
    version=version,
    author="Piotr Dyba",
    author_email="piotr.dyba@localbini.com",
    packages=["lbz", "lbz.dev"],
    scripts=[],
    url="https://github.com/pdyba/lambdalizator",
    license="LICENSE",
    description="AWS Lambda REST ToolBox",
    long_description_content_type="text/markdown",
    long_description=open("README.md").read(),
    install_requires=["python-jose"],
    classifiers=[
        "Environment :: Web Environment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
    ],
    python_requires=">=3.8",
)
