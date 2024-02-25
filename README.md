# Flask-ChatUp
Creating an Flask web chat with socketio, all the javascript code is into HTML because is only testing some features
this project is up on: https://flask-chatup.onrender.com

## Initializing the server
- Clone the repository create an venv and install the dependencies
- $ pip3 install -r requirements.txt
### Run the server
- $ python3 main.py

### Gunicorn deploying
- $ gunicorn --worker-class eventlet -w 1 main:app
