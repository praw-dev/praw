#!/bin/bash

dir=$(dirname $0)

# PEP 8
output=$(find $dir -name \*.py -exec pep8 {} \;)
if [ -n "$output" ]; then
    echo "---pep8---"
    echo -e "$output"
    exit 1
fi

echo "--pylint--"
pylint --rcfile=$dir/.pylintrc $dir/reddit 2> /dev/null
echo

echo "---pyflakes---"
find $dir -name \*.py -exec pyflakes {} \;

exit 0