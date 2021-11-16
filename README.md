You need Python3 and SQLite (including CLI version) installed on your machine.

To run the project you need to execute Run_ticket_creation.bash file in bash CLI using following steps.

Step 1. Open bash CLI.
Step 2. Change current directory to the directory where the project is downloaded and saved 
        cd <path to project directory>
Step 3. bash ./Run_ticket_creation.bash arg1 arg2 arg3
        where,
		     arg1 = Number of tickets to be generated. Must be an integer. e.g. 11
			 arg2 = Name of output json file. e.g. Activities.json
			 arg3 = Path to sqlite folder with name of db that you want to create. e.g. /c/sqlite/db/CRM.db
