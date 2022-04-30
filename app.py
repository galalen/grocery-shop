import os
from datetime import timedelta
from dotenv import load_dotenv
from flask import Flask
from flask_jwt_extended import JWTManager

from blueprints.user import user_api

load_dotenv()

app = Flask(__name__)
app.config['DEBUG'] = os.getenv('DEBUG')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config["JWT_SECRET_KEY"] = os.getenv('SECRET_KEY')
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(hours=48)
jwt = JWTManager(app)

BAS_API = '/api/v1'
app.register_blueprint(user_api, url_prefix=f"{BAS_API}/user")

if __name__ == '__main__':
    app.run(port=os.getenv('FLASK_PORT'))
