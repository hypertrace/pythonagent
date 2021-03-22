from flask import Flask
from threading import Thread
from time import sleep

app = Flask(__name__)

stop_run = False


def my_function():
    global stop_run
    while not stop_run:
        sleep(1)
        print("running...")


def manual_run():
    t = Thread(target=my_function)
    t.start()
    return "Processing"


@app.route("/stop", methods=['GET'])
def set_stop_run():
    global stop_run
    stop_run = True
    return "Application stopped"


@app.route("/run", methods=['GET'])
def run_process():
    global stop_run
    stop_run = False
    return Response(manual_run(), mimetype="text/html")


if __name__ == "__main__":
    app.run()
