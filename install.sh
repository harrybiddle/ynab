#! /bin/bash

set -euo pipefail

# requires poetry and pip
command -v poetry >/dev/null 2>&1 || { echo "Error: requires poetry" > /dev/stderr ; exit 1; }
command -v pip >/dev/null 2>&1 || { echo "Error: requires pip" > /dev/stderr ; exit 1; }

cd "$( dirname "${BASH_SOURCE[0]}" )"  # move into script directory

# clear previous installs
if [ -e dist ] ; then
  rm dist/ynab-*.tar.gz
  rmdir dist
fi

# build and install
poetry build --format sdist
pip3 install --user dist/*
