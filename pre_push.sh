#!/bin/bash

dir=$(dirname $0)

# flake8
flake8 --exclude=docs
if [ $? -ne 0 ]; then
    echo "Exiting due to flake8 errors. Fix and re-run to finish tests."
    exit $?
fi

# pydocstyle
pydocstyle praw
if [ $? -ne 0 ]; then
    echo "Exiting due to pydocstyle errors. Fix and re-run to finish tests."
    exit $?
fi

# pylint
output=$(pylint --rcfile=$dir/.pylintrc $dir/praw 2> /dev/null)
if [ -n "$output" ]; then
    echo "--pylint--"
    echo -e "$output"
fi


exit 0
