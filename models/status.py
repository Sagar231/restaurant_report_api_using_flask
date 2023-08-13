from db import db


class StatusModel(db.Model):
    __tablename__ = "status"
    
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    timestamp_utc = db.Column(db.DateTime, nullable=False)    
   


    





