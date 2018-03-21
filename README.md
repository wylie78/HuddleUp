# HuddleUp
## Setup:
Install python - any version after 2.7 would be good. Then install `pip` which we will use for Python package management.

Run the following commands:
1) Install Flask `pip install Flask`
2) Install SQLAlchemy `pip install SQLAlchemy`

More info: http://flask.pocoo.org/docs/0.12/installation/

## Run:
Run the following commands in the project root directory:
1) `export FLASK_APP=huddleup.py`
2) `flask initdb` (Note: this command initializes the database and only needs to be run if the database has not yet been initialized)
3) `flask run`