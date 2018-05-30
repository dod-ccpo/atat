
# ATST

[![Build Status](https://travis-ci.org/dod-ccpo/atst.svg?branch=master)](https://travis-ci.org/dod-ccpo/atst)

## Installation

    ./script/setup

## Running (development)

Turn on the virtual environment:

    . .venv/bin/activate

Note: you may want to use something like [direnv](https://direnv.net)
or [autoenv](https://github.com/kennethreitz/autoenv) to automate this.

Start the app and watch for changes:

    DEBUG=1 ./app.py

## Testing

To run unit tests:

    ./script/test

or

    python -m pytest

or

    make test

## Notes

tornado templates are like mustache templates -- add the
following to `~/.vim/filetype.vim` for syntax highlighting:

    :au BufRead *.html.to set filetype=mustache

