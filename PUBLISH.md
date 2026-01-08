# Publishing to PyPI

## Refactoring for publishing

- the code was moved under `src` in a folder matching the name of the module, which will be `observability_testing_tool`
- the `pyproject.toml` file was created to configure the metadata, dependencies and build services needed to package and submit the project to PyPi
  - Useful links
    - https://packaging.python.org/en/latest/overview/
    - https://packaging.python.org/en/latest/tutorials/packaging-projects/
    - https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
    - https://setuptools.pypa.io/en/latest/userguide/quickstart.html
    - https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html
- in order to install the dependencies needed for the build specified in the TOML file in the `[project.optional-dependencies]` section, run this command from the folder containing the `pyproject.toml` file
  ```shell
  pip install .[build]
  ```
  - the `--use-pep517` flag forces `pip` to follow PEP 517, which in our case means ensuring that the build dependencies from `[build-system]` are installed

### Development environment

If your `pyproject.toml` file includes an optional dependencies section, for example

```toml
[project.optional-dependencies]
dev = ["pytest", "black", "mypy"]
docs = ["sphinx", "mkdocs"]
test = ["pytest", "coverage"]
```

you can ensure installation of each optional block of dependencies in the following manner, with one or more blocks separated by commas in square brackets. For example, to install _dev_ and _docs_ dependencies

```shell
pip install -e .[dev,docs]
```

NB: the `-e` flag stands for _editable mode_ and effectively links the package to your source code, so that any changes you make are effective immediately. This is very useful for development.

## How to build and submit

- create a new venv for the development, build and publication of the project
  ```shell
  python3 -m venv .venv
  source .venv/bin/activate
  ```
- make sure all dependencies are installed in the Python venv
  ```shell
  pip3 install -e ".[build]"
  ```
- build the project artifacts and metadata
  ```shell
  python3 -m build
  ```
- submit the artifacts and metadata to the index server
  - in test
    ```shell
    python3 -m twine upload --repository testpypi dist/*
    
    # for more detailed output
    python3 -m twine upload --verbose --repository testpypi dist/*
    ```
  - in production
    ```shell
    python3 -m twine upload dist/*

    # for more detailed output
    python3 -m twine upload --verbose dist/*
    ```

### Twine configuration file

You can create a configuration file in your home directory `~/.pypirc` with contents like this

```toml
[distutils]
  index-servers =
    testpypi
    obstool

[obstool]
  repository = https://upload.pypi.org/legacy/
  username = __token__
  password = # your project-specific token for prod

[testpypi]
  username = __token__
  password = # your generic token for test
```

You would then be able to build for the production index server with

```shell
python3 -m twine upload --repository obstool dist/*
```

# Verifying the PyPI installation

Once uploaded, it is critical to verify the package works by installing it in a fresh environment.

## From TestPyPI

**Note:** _TestPyPI often lacks the dependencies found on the main index. You may need to specify the main PyPI index as a fallback._

```shell
# Create a fresh verification venv
python3 -m venv .venv-verify
source .venv-verify/bin/activate

# Install from TestPyPI, falling back to main PyPI for dependencies
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ observability_testing_tool
```

## From PyPI in production

```shell
pip install observability_testing_tool
```

# Version Management

PyPI is immutable. You cannot overwrite a version once it is uploaded. Before running the build and submitting commands again, you must update the version number in `pyproject.toml` (and `src/observability_testing_tool/__init__.py` if you are hardcoding it there).

1. Bump version in `pyproject.toml` : `0.0.1` -> `0.0.2`

2. Clean previous builds: `rm -rf dist/`

3. Re-run build and upload steps.

