from flask import Flask, url_for
import logging
from logging.handlers import RotatingFileHandler
import sys
import requests
from contextlib import redirect_stderr
from flask import request
from flask import jsonify
import threading
import time
app = Flask(__name__)

runningPort = 5000
listOfClients = []

RETRY_COUNT = 5

def heartbeatTo(ipAddr, port):
    time.sleep(5)
    currTries = 0
    while currTries < RETRY_COUNT:
        try:
            print("INFO: Attempting HB to " + ipAddr + ":" + str(port))
            requests.head('http://' + ipAddr  + ':' + str(port) + '/')
        except requests.exceptions.RequestException as e:
            print("WARN: Client " + ipAddr + ":" + str(port) + " failed to HB (" +
                    str(currTries) + ")")
            currTries = currTries + 1
            time.sleep(5)
            continue
        break
    if currTries == RETRY_COUNT:
        listOfClients.remove((ipAddr, port))
        print("WARN: Client " + ipAddr + ":" + str(port) + " removed!")
    threading.Timer(3, heartbeatTo, [ipAddr, port]).start()

@app.route('/register/<port>')
def register_client(port):
    if (request.remote_addr, int(port)) not in listOfClients:
        listOfClients.append((request.remote_addr, int(port)))
        print("GET: Registered " + request.remote_addr + ":" + str(port))
        t1 = threading.Thread(target = heartbeatTo, args = (request.remote_addr, int(port)))
        t1.start()
        return "Registered " + str(port)
    else:
        print("GET: Already registered " + request.remote_addr + ":" + str(port))
        return "Already registered" + str(port)

@app.route('/registered')
def registered_clients():
    return str(listOfClients)

@app.route('/log')
def give_log():
    print("GET: Log")
    data = ''
    with open(str(runningPort)+'server.log', 'r') as myfile:
        data=myfile.read().replace('\n', '</br>')
    return data

@app.route('/search/<query>')
def search_log(query):
    print("GET: Running log search...")
    result = ''
    for x in listOfClients:
        logString = requests.get('http://'+str(x[0])+':'+str(x[1])+'/log').content
        logArray = logString.decode("utf-8").split('</br>')
        for y in logArray:
            if query in y:
                result = result + x[0] + ":" + str(x[1]) + "  ->  " + y + "\n"
    return result

if __name__ == '__main__':
    if len(sys.argv) is not 2:
        print("INIT: Invalid args! Usage is: client.py [port]")
    else:
        print("INIT: Starting Server")
        runningPort = int(sys.argv[1])
        app.debug = True
        app.logger.setLevel(logging.DEBUG)
        with open(str(runningPort)+'server.log', 'w') as stderr, redirect_stderr(stderr):
            app.run(host='localhost', port=runningPort, use_reloader=False)
