#!/bin/bash

DIRECTORY=$1
VERSION=0.15

cp -a $1 `pwd`/cas-$VERSION
tar cvzf cas-$VERSION.tar.gz cas-$VERSION
