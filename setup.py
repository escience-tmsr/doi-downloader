"""Python setup.py for doi_downloader package"""
import io
import os
from setuptools import find_packages, setup


def read(*paths, **kwargs):
    """Read the contents of a text file safely.
    >>> read("doi_downloader", "VERSION")
    '0.1.0'
    >>> read("README.md")
    ...
    """

    content = ""
    with io.open(
        os.path.join(os.path.dirname(__file__), *paths),
        encoding=kwargs.get("encoding", "utf8"),
    ) as open_file:
        content = open_file.read().strip()
    return content


def read_requirements(path):
    return [
        line.strip()
        for line in read(path).split("\n")
        if not line.startswith(('"', "#", "-", "git+"))
    ]


setup(
    name="doi_downloader",
    version="0.1.0",
    packages=find_packages(exclude=["tests", ".github"]),
    # version=read("doi_downloader", "VERSION"),
    description="Awesome doi_downloader created by escience-cosmas",
    # url="https://github.com/escience-cosmas/doi-downloader/",
    # long_description=read("README.md"),
    # long_description_content_type="text/markdown",
    author="escience-tmsr",
    # packages=find_packages(exclude=["tests", ".github"]),
    install_requires=read_requirements("requirements.txt"),
    # install_requires=[],
    # entry_points={
    #     "console_scripts": ["doi_downloader = doi_downloader.__main__:main"]
    # },
    # extras_require={"test": read_requirements("requirements-test.txt")},
)
