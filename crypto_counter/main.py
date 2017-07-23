from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello():
    return "hello"


@app.route('/balance')
def get_balance():
    pass


@app.route('/markets')
def get_makrets():
    pass
