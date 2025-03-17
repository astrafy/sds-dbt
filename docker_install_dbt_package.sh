#! /bin/sh


local_packages_dir=/app

[  -z "$1" ] && package='*' || package=$1

echo "Installing deps"
echo "Local package dir:: $local_packages_dir"

for dir in $local_packages_dir/$package; do
    echo "Installing deps for $dir"
    cd "$dir"
    dbt deps --profiles-dir=/app
done