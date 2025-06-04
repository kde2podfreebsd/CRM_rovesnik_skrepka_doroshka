#!/bin/bash

db_name='root'
db_user='root'
db_host='172.24.0.3'
backup_folder=$PWD/db_backups

keep_day=30

sqlfile=$backup_folder/database-$(date +%d-%m-%Y_%H-%M-%S).sql
zipfile=$backup_folder/database-$(date +%d-%m-%Y_%H-%M-%S).zip
mkdir -p $backup_folder

if pg_dump -U $db_user -h $db_host $db_name > $sqlfile ; then
   echo 'Sql dump created'
else
   echo 'pg_dump return non-zero code | No backup was created!'
   exit
fi

if gzip -c $sqlfile > $zipfile; then
   echo 'The backup was successfully compressed'
else
   echo 'Error compressing backup | Backup was not created!'
   exit
fi
rm $sqlfile
echo $zipfile

find $backup_folder -mtime +$keep_day -delete
