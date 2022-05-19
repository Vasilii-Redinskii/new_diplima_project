from app import db
from datetime import datetime
from flask import url_for


class Auto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    description = db.Column(db.String())    
    price = db.Column(db.Float)
    transmission = db.Column(db.Boolean)
    img_url_1 = db.Column(db.String(128))
    img_url_2 = db.Column(db.String(128))
    img_url_3 = db.Column(db.String(128))
    img_url_4 = db.Column(db.String(128))
    in_rent_or_free = db.Column(db.Boolean, default=False)
    all_time_rent = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.now)
    total_cost_of_rent = db.Column(db.Float)
    count_rent = db.Column(db.Integer)
    arenda = db.relationship('Arenda', backref='auto', cascade='all,delete')
    image = db.relationship('Image', backref='auto', cascade='all,delete')

    @property
    def logo_url(self):
        return f'/static/{self.logo}' if self.logo else ''


    def get_absolute_url(self):
        return url_for('auto_detail', auto_id=self.id)


class Arenda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    auto_id = db.Column(db.Integer, db.ForeignKey('auto.id'))
    date_rent = db.Column(db.DateTime, default=datetime.now)
    date_free = db.Column(db.DateTime, default=datetime.now)
    in_rent_or_free = db.Column(db.Boolean, default=False)
    time_rent = db.Column(db.Float)
    cost_of_rent = db.Column(db.Float)


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    auto_id = db.Column(db.Integer, db.ForeignKey('auto.id'))
    img_url = db.Column(db.String(128))

    def __repr__(self):
        return self.img_url
