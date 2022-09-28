#!/bin/bash

# Purpose - Download Starbucks stores csv file and insert it into MongoDB.

if test -f "$FILE"; then
  rm stores.csv
fi
mongo "$1" --eval 'db.'"$2"'.drop()'
wget https://raw.githubusercontent.com/chrismeller/StarbucksLocations/master/stores.csv
mongoimport -d "$1" -c "$2" --type csv --file stores.csv --headerline
rm stores.csv
