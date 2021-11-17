#!/usr/bin/bash

pip install -r requirements.txt;

python Create_Random_Tickets_Data.py -i $1 -o $2 ;

python Create_Tables.py -p $3 -j $2 ;

sqlite3 $3 < Generate_Stats.sql;



