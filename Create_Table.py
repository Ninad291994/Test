#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import json
import sqlite3
from sqlite3 import Error
import numpy as np
import argparse
import sys

sqlite3.register_adapter(np.int64, lambda val: int(val))
sqlite3.register_adapter(np.int32, lambda val: int(val))


# In[3]:


def create_dataframes_from_json(json_file):
    try:
        data = json.load(open(json_file))
    
    except Error as e:
        sys.exit(e) 
        
    df_metadata = pd.DataFrame([data["metadata"]])
    
    df_tickets = pd.DataFrame()
    for i in data["activities_data"]:
        df_tickets = df_tickets.append(pd.DataFrame([i]), ignore_index = True)
    
    df_temp = pd.json_normalize(df_tickets["activity"])
    df_activity = pd.concat([df_tickets[["ticket_id"]], df_temp], axis=1)
    
    df_note = df_activity[["ticket_id", "Note.id", "Note.type", "Note.description"]]
    
    df_tickets = df_tickets[["ticket_id", "performer_id", "performed_at", "performer_type"]]

    df_activity = df_activity[['ticket_id', 'shipping_address', 'shipment_date', 'category',
                               'contacted_customer', 'issue_type', 'source', 'status', 'priority',
                               'group', 'agent_id', 'requester', 'product']]


    df_activity = df_activity[df_activity['shipping_address'].notna()]

    df_note = df_note[df_note['Note.id'].notna()]
    
    return df_metadata, df_tickets, df_activity, df_note


# In[4]:


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
        
    return conn


# In[5]:


def create_queries():
    
    m = """DROP TABLE IF EXISTS Metadata;"""
    t = """DROP TABLE IF EXISTS Tickets;"""
    a = """DROP TABLE IF EXISTS Activity;"""
    n = """DROP TABLE IF EXISTS Note;"""
    
    create_metadata_table = """CREATE TABLE IF NOT EXISTS Metadata (
                                        id INTEGER PRIMARY KEY,
                                        start_date DATETIME NOT NULL,
                                        end_date DATETIME NOT NULL,
                                        activity_count INTEGER NOT NULL
                                    ); """
    create_tickets_table = """CREATE TABLE IF NOT EXISTS Tickets (
                                        ticket_id INTEGER PRIMARY KEY,
                                        performer_id INTEGER NOT NULL,
                                        performer_type TEXT NOT NULL,
                                        performed_at DATETIME NOT NULL
                                    ); """
    
    create_activity_table = """CREATE TABLE IF NOT EXISTS Activity (
                            activity_id   INTEGER PRIMARY KEY,
                            ticket_id   INTEGER NOT NULL,
                            shipping_address TEXT NULL,
                            shipment_date DATE NULL,
                            category TEXT NULL,
                            contacted_customer TEXT NULL,
                            issue_type TEXT NULL,
                            source INTEGER NULL, 
                            status TEXT NOT NULL, 
                            priority INTEGER NULL, 
                            group_type TEXT NULL, 
                            agent_id INTEGER NOT NULL,
                            requester INTEGER NOT NULL, 
                            product TEXT NULL, 
                            FOREIGN KEY (ticket_id)
                               REFERENCES Tickets(ticket_id) 
                        );"""
    
    create_note_table = """CREATE TABLE IF NOT EXISTS Note (
                                        note_id INTEGER PRIMARY KEY,
                                        ticket_id INTEGER NOT NULL,
                                        note_type TEXT NULL,
                                        description TEXT NULL,
                                        FOREIGN KEY (ticket_id)
                                           REFERENCES Tickets(ticket_id) 
                                    ); """
    
    return m, t, a, n, create_metadata_table, create_tickets_table, create_activity_table, create_note_table


# In[6]:


def insert_metadata(c, df_metadata):
    for i in range(len(df_metadata)):
        c.execute("""INSERT INTO Metadata (start_date, end_date, activity_count)
                         VALUES (?, ?, ?); """, (df_metadata.iloc[i][0], df_metadata.iloc[i][1], df_metadata.iloc[i][2]))

def insert_tickets(c, df_tickets):
    for i in range(len(df_tickets)):
        c.execute("""INSERT INTO Tickets (ticket_id, performer_id, performer_type, performed_at)
                         VALUES (?, ?, ?, ?); """, (df_tickets.iloc[i][0], df_tickets.iloc[i][1], df_tickets.iloc[i][3], df_tickets.iloc[i][2]))

        

def insert_activity(c, df_activity): 
    for i in range(len(df_activity)):
        c.execute("""INSERT INTO Activity (ticket_id,
                    shipping_address,
                    shipment_date,
                    category ,
                    contacted_customer,
                    issue_type,
                    source, 
                    status, 
                    priority, 
                    group_type, 
                    agent_id,
                    requester, 
                    product)VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?); """, 
                      (df_activity.iloc[i][0], df_activity.iloc[i][1], df_activity.iloc[i][2],
                      df_activity.iloc[i][3], df_activity.iloc[i][4], df_activity.iloc[i][5],
                      df_activity.iloc[i][6], df_activity.iloc[i][7], df_activity.iloc[i][8],
                      df_activity.iloc[i][9], df_activity.iloc[i][10], df_activity.iloc[i][11],
                      df_activity.iloc[i][12]))


def insert_note(c, df_note):
    for i in range(len(df_note)):
        c.execute("""INSERT INTO Note (note_id, ticket_id, note_type, description)
                         VALUES (?, ?, ?,?); """, (df_note.iloc[i][1], df_note.iloc[i][0], df_note.iloc[i][2], df_note.iloc[i][3]))


# In[8]:


def main(path, json_file):
    df_metadata, df_tickets, df_activity, df_note = create_dataframes_from_json(json_file)
    
    
    m, t, a, n, create_metadata_table, create_tickets_table, create_activity_table, create_note_table = create_queries()
    
    conn = create_connection(path)
    
    if conn is not None:
        try:
            c = conn.cursor()
            # drop all tables
            c.execute(m)
            c.execute(t)
            c.execute(a)
            c.execute(n)

            # create metadata table
            c.execute(create_metadata_table)

            # create tickets table
            c.execute(create_tickets_table)

            # create metadata table
            c.execute(create_activity_table)

            # create tickets table
            c.execute(create_note_table)

            # insert data from dataframe into Metadata table
            insert_metadata(c, df_metadata)

            # insert data from dataframe into Tickets table
            insert_tickets(c, df_tickets)

            # insert data from dataframe into Activity table
            insert_activity(c, df_activity)

            # insert data from dataframe into Note table
            insert_note(c, df_note)

            # Commit changes in the database
            conn.commit()
        
        except Error as e:
            # Rollback changes in the database
            conn.rollback()
            print(e)
        
        finally:
            # Closing the connection
            conn.close()
        
    else:
        print("Error! cannot create the database connection.")
        
    


# In[9]:


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Execute from command line')
    parser.add_argument("-p", type=str, required=True, help="Path to sqlite folder where target db is to be created e.g. C:\sqlite\db\name_of_db.db")
    parser.add_argument("-j", type=str, required=True, default="activities.json", help="JSON file name to be read.")

    args = parser.parse_args()

    path = args.p
    json_file = args.j
    main(path, json_file)


# In[ ]:




