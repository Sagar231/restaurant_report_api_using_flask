from db import db


class TimezoneModel(db.Model):
    __tablename__ = "timezone"

    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.String(50), nullable=False)
    timezone_str = db.Column(db.String(50))
