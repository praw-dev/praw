#!/bin/bash

dir=$(dirname $0)

# flake8
flake8 --exclude=docs
if [ $? -ne 0 ]; then
    echo "Exiting due to flake8 errors. Fix and re-run to finish tests."
    exit 1
fi

# pydocstyle
pydocstyle praw
if [ $? -ne 0 ]; then
    echo "Exiting due to pydocstyle errors. Fix and re-run to finish tests."
    exit 1
fi

# sphinx
rm -rf /tmp/_praw_sphinx 2> /dev/null
sphinx-build -W docs/ /tmp/_praw_sphinx
if [ $? -ne 0 ]; then
    echo "Exiting due to sphinx-buld errors. Fix and re-run to finish tests."
    exit 1
fi

# pylint
output=$(pylint --rcfile=$dir/.pylintrc $dir/praw 2> /dev/null)
if [ -n "$output" ]; then
    echo "--pylint--"
    echo -e "$output"
    exit 1
fi


exit 0
