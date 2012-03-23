#!/bin/bash

dir=$(dirname $0)

# pep8
output=$(find $dir/reddit -name [A-Za-z_]\*.py -exec pep8 {} \;)
if [ -n "$output" ]; then
    echo "---pep8---"
    echo -e "$output"
    exit 1
fi

# pylint
output=$(pylint --rcfile=$dir/.pylintrc $dir/reddit 2> /dev/null)
if [ -n "$output" ]; then
    echo "--pylint--"
    echo -e "$output"
fi

echo "---pyflakes---"
find $dir/reddit -name [A-Za-z_]\*.py -exec pyflakes {} \;

exit 0