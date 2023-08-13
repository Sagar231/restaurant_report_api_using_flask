from flask.views import MethodView

from flask_smorest import Blueprint, abort
import uuid

from models import StatusModel,StoreTimeModel
from sqlalchemy import extract
import csv
import os
import threading

blp = Blueprint("Stores", __name__, description="Operations on stores")


@blp.route("/trigger_report")
class Store(MethodView):
    @blp.response(200)
    def get(self):
        random_uuid = str(uuid.uuid4())
        with open("report_id.txt","a") as reportfile:
            reportfile.write(f"{random_uuid}")
        return {"report_id": random_uuid}


@blp.route("/get_report/<string:report_id>")
class StoreList(MethodView):
    @blp.response(200)
    def get(self,report_id):
        folder_path = 'report_folder'
        file_name = f'{report_id}.csv' 

        # Check if the file exists in the specified folder
        if os.path.exists(os.path.join(folder_path, file_name)):
            return {'report_status' : 'report is genrated please check the report folder'}
        

        with open('report_id.txt','r') as reportfile:
            lines = reportfile.readlines()
            if report_id in lines:
                report =dict()
                storetime = StoreTimeModel.query.all()
                for store in storetime:
                    report_instance = dict()
                    total_time_last_week = 0
                    uptime_last_week =0
                    store_id = store.store_id
                    minutes_query_active = StatusModel.query \
                                        .with_entities(extract('minute', StatusModel.timestamp_utc)) \
                                        .filter_by(store_id=store_id) \
                                        .filter(StatusModel.status == "active") \
                                        .all()
                    minutes_query_total = StatusModel.query.with_entities(extract('minute', StatusModel.timestamp_utc)).filter_by(store_id=store_id).all()
                
                    for status in minutes_query_total:
                        total_time_last_week+=status[0]
                    for status in minutes_query_active:
                        uptime_last_week+=status[0]
                    downtime_last_week = total_time_last_week-uptime_last_week
                    try:
                        uptime_last_hour = minutes_query_active[-1][0]
                    except IndexError as e:
                        uptime_last_hour = 0
                        print(f'there is and indexerror: {e}')
                    downtime_last_hour = 60 - int(uptime_last_hour)
                    report_instance['store_id'] = store_id
                    report_instance['uptime_last_hour'] = uptime_last_hour
                    report_instance['downtime_last_hour'] = downtime_last_hour
                    report_instance['uptime_last_week'] = round(uptime_last_week/(60*24))
                    report_instance['downtime_last_week'] = round(downtime_last_week/(60*24))
                report[f'{store_id}'] = report_instance
                     
            else:
                abort(
                    400,
                     message="You have provided a wrong report_id.",
                )
            field_names = ['store_id', 'uptime_last_hour','downtime_last_hour','uptime_last_week','downtime_last_week'] 
             # Write the data to a CSV file
            with open(f'report_folder/{report_id}.csv', 'w', newline='') as csvfile:
                csv_writer = csv.DictWriter(csvfile, fieldnames=field_names)
                
                # Write the header row
                csv_writer.writeheader()
                
                # Write the data rows
                for key, values in report.items():
                    csv_writer.writerow(values)
            
            return {'report_status':'genration is complete'}