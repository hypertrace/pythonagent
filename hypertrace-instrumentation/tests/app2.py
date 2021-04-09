# server.py
from collections import defaultdict

import requests

from flask import Flask, request

app = Flask(__name__)
CACHE = defaultdict(int)

@app.route("/")
def fetch():
  url = request.args.get("url")
  CACHE[url] += 1
  resp = requests.get(url)
  return resp.content

@app.route("/cache")
def cache():
  keys = CACHE.keys()
  return "{}".format(keys)

if __name__ == "__main__":
  app.run()
