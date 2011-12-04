#!/bin/bash

dir=$(dirname $0)

# PEP 8
output=$(find $dir -name \*.py -exec pep8 {} \;)
if [ -n "$output" ]; then
    echo "---pep8---"
    echo -e "$output"
    exit 1
fi

echo "---pychecker---"
pychecker --quiet --limit 20 $dir/reddit

echo "---pyflakes---"
find $dir -name \*.py -exec pyflakes {} \;

exit 0