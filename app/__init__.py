from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# Импортируем пакет Migrate для работы с миграциями
from flask_migrate import Migrate

from config import Config


app = Flask(__name__,
            static_url_path='', 
            static_folder='static')

app.config.from_object(Config)

# Создаем саму базу данных - объект db
db = SQLAlchemy(app)

# Создаем объект для работы с миграциями
migrate = Migrate(app, db, render_as_batch=True)

from app import views
from app import models
