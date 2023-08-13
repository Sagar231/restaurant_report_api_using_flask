from flask import Flask
from flask_smorest import Api
from sqlalchemy.exc import IntegrityError
from sqlalchemy import inspect

from db import db
import csv
from datetime import datetime
import models
from resources.stores import blp as StoreBlueprint

def create_app(db_url=None):
    app = Flask(__name__)
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config[
        "OPENAPI_SWAGGER_UI_URL"
    ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or "sqlite:///data.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    db.init_app(app)
    api = Api(app)

    with app.app_context():
        inspector = inspect(db.engine)
        if not inspector.has_table("status"):
            db.create_all()
            with open('data1.csv', 'r') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    timestamp_str = row['timestamp_utc']
                    try:
                        timestamp_utc = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f %Z')
                    except ValueError as e:
                            print(f"Error processing timestamp: {e}")
                            try:
                                timestamp_utc = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                            except ValueError as e:
                                print(f"Error processing timestamp without timezone: {e}")
                    except IntegrityError as e:
                            db.session.rollback()
                            print(f"Integrity Error: {e}")          
                    _status = models.StatusModel(
                                                store_id=row['store_id'],
                                                status=row['status'],
                                                timestamp_utc=timestamp_utc
                                            )
                    db.session.add(_status)
                db.session.commit()

        if not inspector.has_table("storetime"):
            with open('data2.csv', 'r') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    _storetime = models.StoreTimeModel(
                                                    store_id=row['store_id'],
                                                    day_of_week = int(row['day']),
                                                    start_time_local = datetime.strptime(row['start_time_local'], '%H:%M:%S').time(),
                                                    end_time_local = datetime.strptime(row['end_time_local'], '%H:%M:%S').time()
                                                    )
                    db.session.add(_storetime)
                db.session.commit()

        if not inspector.has_table("timezone"):
            with open('data3.csv', 'r') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    _store = models.TimezoneModel(
                                                store_id=row['store_id'],
                                                timezone_str = row['timezone_str']
                                                )
                    db.session.add(_store)
                db.session.commit()

        

    api.register_blueprint(StoreBlueprint)
    return app