DROP TABLE IF EXISTS Ticket_Status_Stats;
DROP TABLE IF EXISTS temp_table;

CREATE TABLE IF NOT EXISTS Ticket_Status_Stats (
                                        id INTEGER PRIMARY KEY,
										ticket_id INTEGER NOT NULL,
										activity_id INTEGER NOT NULL,
                                        time_spent_open DATETIME NULL,
                                        time_spent_waiting_on_customer DATETIME NULL,
                                        time_spent_waiting_for_response DATETIME NULL,
										time_till_resolution DATETIME NULL,
										time_to_first_response DATETIME NULL,
										FOREIGN KEY (ticket_id)
										REFERENCES Tickets(ticket_id),
										FOREIGN KEY (activity_id)
										REFERENCES Activity(activity_id)
                                    );
								
CREATE TABLE temp_table AS 
SELECT T.ticket_id, A.activity_id, strftime('%s','now')- strftime('%s',T.performed_at) AS time, A.status FROM Tickets AS T JOIN Activity AS A ON T.ticket_id = A.ticket_id;



INSERT INTO Ticket_Status_Stats (ticket_id, activity_id, time_spent_open, time_spent_waiting_on_customer, time_spent_waiting_for_response,
time_till_resolution, time_to_first_response)
SELECT T.ticket_id AS ticket_id, T.activity_id AS activity_id, (CASE WHEN T.Status = 'Open' THEN T.time ELSE NULL END) AS time_spent_open, 
(CASE WHEN T.Status IN ('Waiting for Customer', 'Waiting for Third Party') THEN T.time ELSE NULL END) AS time_spent_waiting_on_customer, 
(CASE WHEN T.Status = 'Pending' THEN T.time ELSE NULL END) AS time_spent_waiting_for_response, 
(CASE WHEN T.Status = 'Resolved' THEN T.time ELSE NULL END) AS time_till_resolution, 
(CASE WHEN T.Status = 'Closed' THEN T.time ELSE NULL END) AS time_to_first_response
FROM temp_table AS T;


CREATE TRIGGER UPDATE_STATUS_TIME_TRIGGER
   AFTER UPDATE OF status ON Activity
   WHEN OLD.status <> NEW.status
BEGIN 
   UPDATE Ticket_Status_Stats 
   set time_spent_open = CASE WHEN OLD.status = 'Open' THEN strftime('%s','now')- strftime('%s',(SELECT performed_at FROM Tickets WHERE ticket_id = OLD.ticket_id)) ELSE time_spent_open END,
   time_spent_waiting_for_response = CASE WHEN OLD.status = 'Pending' THEN strftime('%s','now')- strftime('%s',(SELECT performed_at FROM Tickets WHERE ticket_id = OLD.ticket_id)) ELSE time_spent_waiting_for_response END,
   time_spent_waiting_on_customer = CASE WHEN OLD.status = 'Waiting for Customer' THEN strftime('%s','now')- strftime('%s',(SELECT performed_at FROM Tickets WHERE ticket_id = OLD.ticket_id)) ELSE time_spent_waiting_on_customer END,
   time_till_resolution = CASE WHEN OLD.status = 'Resolved' THEN strftime('%s','now')- strftime('%s',(SELECT performed_at FROM Tickets WHERE ticket_id = OLD.ticket_id)) ELSE time_till_resolution END,
   time_to_first_response = CASE WHEN OLD.status = 'Closed' THEN strftime('%s','now')- strftime('%s',(SELECT performed_at FROM Tickets WHERE ticket_id = OLD.ticket_id)) ELSE time_to_first_response END 
   WHERE ticket_id = OLD.ticket_id AND activity_id = OLD.activity_id;
END;


DROP TABLE IF EXISTS temp_table;




