#### Dev Install
```bash
poetry install

# install shot as symlink to avoid reinstall whenever code changes
# instead of pip install /path/to/shot
# https://github.com/python-poetry/poetry/issues/1135
# workaround using __name__ == '__main__' and fire
poetry run task dev
```

#### Tests
```bash
poetry run task tests
```

Tested locally on OSX Mojave 10.14.6

#### Linter
```bash
# to autoformat python code
poetry run task lint

# to sort imports
poetry run task isort
```

#### Version management
```bash
# pass args e.g. patch, minor, major, choose to commit changes or not
poetry run bumpversion --commit --tag patch
```