#!/bin/bash

# Test envirnment folder
mkdir testing
cd testing

touch hi1.txt
touch hi2.txt
touch hi3.txt

rm -f ./*
cd ../
rmdir testing
