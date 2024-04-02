from flask import Flask
import json

app = Flask(__name__)

@app.route("/rotate")
def rotate():
    file = open (r"data\rotate.json", "r")
    data = json.loads(file.read())
    return data

@app.route("/scale")
def scale():
    file = open (r"data\scale.json", "r")
    data = json.loads(file.read())
    return data

@app.route("/remove")
def remove():
    file = open (r"data\remove.json", "r")
    data = json.loads(file.read())
    return data

@app.route("/replace")
def replace():
    file = open (r"data\replace.json", "r")
    data = json.loads(file.read())
    return data
    
    