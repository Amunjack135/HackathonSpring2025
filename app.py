from flask import Flask, request, jsonify, render_template, redirect, url_for, session

import CustomMethodsVI.Connection as Connection
s
app = Flask(__name__)

@app.route("/")
def index():

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)