import os
from dotenv import load_dotenv
from flask import Flask
from flask_pymongo import PyMongo

load_dotenv()

app = Flask(__name__)
app.config['DEBUG'] = os.getenv('DEBUG')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
mongo = PyMongo(app)


if __name__ == '__main__':
    app.run(port=os.getenv('FLASK_PORT'))
