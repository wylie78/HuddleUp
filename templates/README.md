# HuddleUp
## Setup:
Install python - any version after 2.7 would be good. 
1) `brew install python3`

Then install `pip` which we will use for Python package management, run the following command:
1) `sudo easy_install pip`

Run the following commands:
1) Install Flask `sudo pip install Flask`
2) Install SQLAlchemy `sudo pip install SQLAlchemy`
3) Install SQLAlchemy Flask extension `sudo pip install Flask-SQLAlchemy`

More info: http://flask.pocoo.org/docs/0.12/installation/

## Run:
Run the following commands in the project root directory:
1) `export FLASK_APP=huddleup.py`
2) `flask initdb` (Note: this command initializes the database and only needs to be run if the database has not yet been initialized)
3) `flask run`