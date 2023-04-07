#!/bin/bash

PathBackups=$HOME/DockerVolumeBackups

#Backup a docker volume
function RunBackup () {
    TIMESTAMP=$(date +"%F_%H-%M-%S")
    NAME=Latest_$TIMESTAMP
    VOL_NAME=$1
    mkdir -p $VOL_NAME
    cd ./$VOL_NAME

    echo $NAME
    touch $NAME
    sleep 3

    cd $PathBackups
}

function CleanBackups () {
    VOL_NAME=$1
    cd ./$VOL_NAME

    ls | while read line
    do
        echo $line
    done

    cd $PathBackups
}

#The following line takes the name of every volume and creates a backup.
mkdir -p $PathBackups
cd $PathBackups
docker volume ls -q | while read line
do 
    echo $line
    RunBackup $line 
    CleanBackups $line
    echo ""
done