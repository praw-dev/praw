#!/bin/bash

status=$(git status | head -n 1)
if [[ "$status" != "# On branch master" ]]; then
    echo "Not on master branch. Goodbye"
    exit 1
fi

version1=$(python -c "import reddit; print reddit.VERSION")
version2=$(egrep -o "'[0-9.]+'" setup.py)

if [[ "'$version1'" != $version2 ]]; then
    echo "'$version1' does not match $version2. Goodbye"
    exit 1
fi

read -p "Do you want to deploy $version1? [y/n] " input
case $input in
    [Yy]* ) break;;
    * ) echo "Goodbye"; exit 1;;
esac

python setup.py sdist upload -s
if [ $? -ne 0 ]; then
    echo "Pushing distribution failed. Aborting."
    exit 1
fi

git tag -s $version1 -m "Version $version1"
if [ $? -ne 0 ]; then
    echo "Tagging version failed. Aborting."
    exit 1
fi

git push bboe master --tags
git push mellort master --tags
