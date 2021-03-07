#### Dev Install
```bash
poetry install

# install shot as symlink to avoid reinstall whenever code changes
# instead of pip install /path/to/shot
# https://github.com/python-poetry/poetry/issues/1135
# workaround using __name__ == '__main__' and fire
poetry run task dev
```

#### Git hooks
```bash
poetry run task install_hooks
# use --force to overwrite hooks if they already exist
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
# once the tag is built by the release action, check the attached .tar is installable.
# e.g. `pip install git+https://github.com/ConorSheehan1/shot@v0.1.1`
# if it is update the release draft and pre-release state.
```



#### Approach
Errors are swallowed in favor of user friendly short messages.
Usually wouldn't suppress errors, but traces can be super long, and there shouldn't be much to handle here.
TODO: use rich, then leave exceptions since they'll be formatted?
TODO: add pytest random order plugin