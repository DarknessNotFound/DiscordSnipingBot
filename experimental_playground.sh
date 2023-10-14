#!/bin/bash

# Test envirnment folder
mkdir testing
cd testing

cp -r ../DiscordBot/* ./
cp ../.env

python3 ./main.py

# Cleanup
rm -rf ./*
cd ../
rmdir testing
