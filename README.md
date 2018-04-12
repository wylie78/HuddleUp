
# HuddleUp

## What is HuddleUp?

A SQLite and Flask powered check list app
	  
## Author:
	
Team 8
	  

## How do I use it?
	
1. Install python 3.6.5 or above on your computer.

2. Change to the root directory of HuddleUp app

3. Run the following command to install all dependencies with pip

	`python -m pip install -r requirement.txt`

4. (Optional)edit the configuration in the huddleup.py file or export a HUDDLEUP_SETTINGS environment variable pointing to a configuration file.

5. tell flask about the right application:

	`export FLASK_APP=huddleup.py`
 
	(For windows user, use set command instead)

6. fire up a shell and run this:

	`flask initdb`

7. now you can run HuddleUp:

	`flask run`

8. the application will greet you at `http://localhost:5000/`

