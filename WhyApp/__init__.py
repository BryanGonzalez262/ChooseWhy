import json

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_recaptcha import ReCaptcha

app = Flask(__name__)
config_dir = 'WhyApp/config.json'


with open(config_dir) as config_file:
    config = json.load(config_file)

for K in config.keys():
    app.config[K] = config.get(K)


recaptcha = ReCaptcha(app)
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


from . import views

if __name__ == '__main__':
    app.run()