from setuptools import setup

setup(
    name="lbz",
    version="0.1.1",
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
