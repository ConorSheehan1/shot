# Shot
[![Build Status](https://github.com/ConorSheehan1/shot/workflows/ci/badge.svg)](https://github.com/ConorSheehan1/shot/actions/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tested python versions](https://img.shields.io/badge/dynamic/yaml?url=https://raw.githubusercontent.com/ConorSheehan1/shot/master/.github/workflows/ci.yml&label=Tested%20python%20versions&query=$.jobs.build.strategy.matrix.python)](https://github.com/ConorSheehan1/shot/blob/master/.github/workflows/ci.yml#L13)

**S**creenshot  
**H**elper for  
**O**SX  
**T**erminal 

Copy or move screenshots and recordings around from a terminal.

![shot](./.github/images/shot.png)

# Install
```bash
# option 1 homebrew
brew install conorsheehan1/conorsheehan1/shot

# option 2 github release
pip install https://github.com/ConorSheehan1/shot/releases/latest/download/shot.tar.gz

# option 3 from source
git clone git@github.com:ConorSheehan1/shot.git
cd shot
poetry install
poetry build
pip install .
```

# Example
```bash
shot --help
shot --version

# default is to copy the latest screenshot to the current directory
shot

# copy the last 3 screenshots to ./foo
shot --dst=./foo --num=3

# short args are added automatically when unambiguous e.g. -n and --num
shot -dst ./foo -n 3

# move the second last screenshot to ./bar
shot --mv --dst=./bar --start=2
```

### Smaller bash implementation
https://gist.github.com/ConorSheehan1/2a72b13fa530388dcaec93307f4f7b09
