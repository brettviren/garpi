#!/bin/sh

file=$1
shift
delim=$1

if [ -z "$file" ] ; then
    echo "No file given to source"
    exit 1
fi

if [ ! -f $file ] ; then
    echo "No such file: $file"
    exit 1
fi

. $file && echo $delim && env
