#!/bin/bash

dir=$(dirname $0)

# pep8
output=$(find $dir/praw -name [A-Za-z_]\*.py -exec pep8 {} \;)
if [ -n "$output" ]; then
    echo "---pep8---"
    echo -e "$output"
    exit 1
fi

# pylint
output=$(pylint --rcfile=$dir/.pylintrc $dir/praw 2> /dev/null)
if [ -n "$output" ]; then
    echo "--pylint--"
    echo -e "$output"
    exit 1
fi

echo "---pyflakes---"
find $dir/praw -name [A-Za-z_]\*.py -exec pyflakes {} \;

# pep257
find $dir/praw -name [A-Za-z_]\*.py | xargs pep257

exit 0