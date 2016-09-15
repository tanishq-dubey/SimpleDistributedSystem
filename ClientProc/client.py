from flask import Flask
import logging
from logging.handlers import RotatingFileHandler
import sys
from contextlib import redirect_stderr
import requests
app = Flask(__name__)

runningPort = 5000

@app.route('/')
def hello_world():
    print("GET: HB")
    return str(runningPort)

@app.route('/log')
def give_log():
    print("GET: Log")
    data = ''
    with open(str(runningPort)+'.log', 'r') as myfile:
        data=myfile.read().replace('\n', '</br>')
    return data


if __name__ == '__main__':
    if len(sys.argv) is not 2:
        print("ERROR: Invalid args! Usage is: client.py [port]")
    else:
        print("Starting Server")
        runningPort = int(sys.argv[1])
        print("INIT: Connecting to master...")
        try:
            requests.head('http://localhost:5000/register/'+str(runningPort))
        except requests.exceptions.RequestException as e:
            print("ERROR: Could not connect to master")
            sys.exit(1)
        print("INIT: Connection Success!")
        app.debug = True
        app.logger.setLevel(logging.DEBUG)
        with open(str(runningPort)+'.log', 'w') as stderr, redirect_stderr(stderr):
            app.run(host='localhost', port=runningPort,  use_reloader=False)

