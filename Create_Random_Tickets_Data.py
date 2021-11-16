#!/usr/bin/env python
# coding: utf-8

# In[2]:


from datetime import datetime, timezone, timedelta
import random
import sys
import argparse
import json
import string

random.seed(1)


# In[ ]:


def generate_random_numbers(num_tickets, unique):
    if unique == True:
        return random.sample(range(1, sys.maxsize), num_tickets)
    else:
        l = []
        for i in range(num_tickets):
            l.append(random.randint(1, sys.maxsize))
        return l

def generate_random_datetime(with_time = True):
    if with_time == True:
        hours = random.randint(0, 23)
        minutes = random.randint(0, 60)
        seconds = random.randint(0, 60)
        microsec = random.randint(0, 1000000)

        today = datetime.now(timezone.utc)
        random_date = today - timedelta(hours=hours, minutes=minutes, seconds=seconds, microseconds=microsec)
        return random_date.isoformat()
    else:
        day = random.randint(0, 7)
        today = datetime.now(timezone.utc)
        random_date = today - timedelta(days=day)
        random_date = random_date.date().isoformat()
        random_date = datetime.strptime(random_date, '%Y-%m-%d').strftime('%d-%b-%Y')
        return random_date
    
def generate_random_activity(performer_id, note_id_list):
    r = random.choice(['a', 'b'])
    i = random.choice([0, 1])
    if r == 'a':
        shipping_address = str(random.randint(0,30))+','+' '+''.join(random.sample(string.ascii_lowercase,10))+','+' '+ str(random.randrange(1000, 10000, 4))
        shipment_date = generate_random_datetime(False)
        contacted_customer = random.choice([True, False])
        source = random.randint(1, 4)
        priority = random.randint(1, 4)
        group = random.choice(['refund', 'partial refund', 'replacement'])
        agent_id = performer_id
        requester = random.randint(1, sys.maxsize)
        issue_type = random.choice(['Incident', 'Problem', 'Change'])
        status = random.choice(['Open','Closed', 'Resolved', 'Waiting for Customer', 'Waiting for Third Party', 'Pending'])
        
        p = list(random.choice([{'phone':['Smartphone','Conventional']}, {'Computer':['Desktop', 'Laptop']}, {'TV':['Conventional', 'Smart TV']}]).items())[0]
        category = p[0]
        Product = p[1][i]
        activity= {"shipping_address": shipping_address, "shipment_date": shipment_date, "category": category, "contacted_customer": contacted_customer,
                    "issue_type": issue_type,
                    "source": source,
                    "status": status,
                    "priority": priority,
                    "group": group,
                    "agent_id": performer_id,
                    "requester": requester,
                    "product": Product}
        
        return activity
    
    else:
        idx = random.choice(note_id_list)
        note_id_list.remove(idx)
        type_of_note = random.randint(1, 4)
        description = random.choice(['', ''.join(random.sample(string.ascii_lowercase,20))])
        activity = { "Note":{"id":idx,"type":type_of_note, "description":description}} 
        return activity


# In[ ]:


def dict_construct(num_tickets, output_file):
    
    # Generate random start date and end date. All the tickets generated will fall between this datetime range.
    # Let's take datetime range of 1 day (24 hrs). The actaul datetime range would be of past 24 hrs when this code is executed.
    today = datetime.now(timezone.utc)
    yesterday = today - timedelta(days=1)
    
    # Create parent dictionary with two keys: 
    # 1. metadata - which holds sub-dictionary of datetime range in which all the tickets fall and number of tickets to be generated.
    # 2. activities_data - which holds list actual tickets
    ticket_activities = {"metadata": {"start_at": yesterday.isoformat(), 
                                  "end_at": today.isoformat(), 
                                  "activities_count": num_tickets},
                         "activities_data":[]}
    
    
    # Generate unique random integers for attributes of ticket
    ticket_id_list = generate_random_numbers(num_tickets, True)
    performer_id_list = generate_random_numbers(num_tickets, False)
    note_id_list =  generate_random_numbers(num_tickets, True)
    
    # Generate activities_data list of sub-dictionaries
    for ticket_id, performer_id in zip(ticket_id_list, performer_id_list):
        performed_at = generate_random_datetime()
        activity = generate_random_activity(performer_id, note_id_list)
        
        each_ticket_dict = {"performed_at": performed_at,"ticket_id": ticket_id, "performer_type": "user",
                                "performer_id": performer_id,"activity":activity}
        
        
        ticket_activities["activities_data"].append(each_ticket_dict)
     
    # Save dictionary created in JSON file
    with open(output_file, 'w') as js:
        json.dump(ticket_activities, js)


# In[ ]:


def main():
    parser = argparse.ArgumentParser(description='Execute from command line')
    parser.add_argument("-i", type=int, required=True, help="Number of tickets to be generated. Number must be an integer.")
    parser.add_argument("-o", type=str, default="activities.json", help="Output JSON file name ending with .json")

    args = parser.parse_args()

    num_tickets = args.i
    output_file = args.o
    
    if num_tickets <= (sys.maxsize / 2) - 1:
        dict_construct(num_tickets, output_file)
    else:
        print("Number of tickets to be generated must be less than %i", sys.maxsize / 2)
    


# In[ ]:


if __name__ == "__main__":
    main()

