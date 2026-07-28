# `doi-downloader` developer documentation

If you're looking for user documentation, go [here](README.md).

## Development install

```shell
# Create a virtual environment, e.g. with
make virtualenv

# activate virtual environment
source env/bin/activate

# make sure to have a recent version of pip and setuptools
python -m pip install --upgrade pip setuptools

# (from the project root directory)
# install doi-downloader as an editable package
python -m pip install --no-cache-dir --editable .
# install development dependencies
python -m pip install -r requirements-test.txt
```

## Running the tests

With the development environment installed and activated, you can run the tests with

```shell
make test
```

This first lints the code, and then runs the tests in a 'fail-fast' mode with coverage.
To see the coverage results on the command line, run

```shell
coverage report
```

`coverage` can also generate output in HTML and other formats; see `coverage help` for more information.## Running linters locally

## Pre-commit hooks

This repository includes a configuration for various [pre-commit](https://pre-commit.com) hooks.
They check for formatting and style consistency of various files, ensuring that the repository
remains clean and consistent. Each hook runs fast, and most of them will fix any problems they find.
Several checks will only run if relevant files have been changed.
You can install it as follows:

```shell
python -m pip install pre-commit  # only needed if you didn't already install requirements-test.txt
pre-commit install
```

To manually run the checks:

```shell
pre-commit run  # runs the checks as if you were about to create a commit, may skip some
pre-commit run --all  # runs all checks without skipping any
```

## Linters

For linting and sorting imports we will use [ruff](https://docs.astral.sh/ruff/). Running the linters requires an
activated virtual environment with the development tools installed.

```shell
make lint
```

To apply the linter's fixes, you can run

```shell
ruff check --fix doi_downloader
```

It also provides a command to apply the formatter provided by `ruff`, to ensure a consistent code style:

```shell
make fmt
```
