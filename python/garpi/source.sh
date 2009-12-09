#!/bin/sh

file=$1
shift
delim=$1

. $file && echo $delim && env
