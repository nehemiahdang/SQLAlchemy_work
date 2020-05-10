# Import Flask
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Grabbing code from jupyter notebook
# Query for Date & Prcp
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(bind=engine)
date_prcp_last_12 = session.query(Measurement.date, Measurement.prcp).\
                    filter(Measurement.date >= '2016-08-23').\
                    order_by(Measurement.date).all()
date_last_12 = []
prcp_last_12 = []

for data in date_prcp_last_12:
    if type(data.prcp) == float:
        date_last_12.append(data.date)
        prcp_last_12.append(data.prcp)                    
# -------------------------------------------
# Query Stations
station_list = []

unique_stations = session.query(Station.name, func.count(Station.name)).\
                    group_by(Station.name).all()
for data in unique_stations:
    station_list.append(data[0])
# -------------------------------------------
# Query for Temperature Observations (TOBS) in the last year
pre_join = [Measurement.date, Measurement.tobs]
same_station = session.query(*pre_join).\
                filter(Measurement.station == Station.station).\
                filter(Station.name == 'WAIHEE 837.5, HI US').\
                filter(Measurement.date >= '2016-08-18').all()

date_list = []
tobs_list = []
for data in same_station:
    date_list.append(data[0])           
    tobs_list.append(data[1])   

date_tobs_dict = {
    "Date": date_list,
    "TOBS": tobs_list}

# Creating a dictionary from the data I queried
climate_dict = [
    {"date": date_last_12},
    {"prcp": prcp_last_12}
]

# Creating an app
app = Flask(__name__)

# Defining what happens when user uses index route
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        f"Welcome to Climate API!<br/>"
        f"Here's are the available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"Please replace the 'start' with a date yyyy-mm-dd anywhere between 2016-08-18 and 2017-08-18<br/>"
        f"/api/v1.0/start/end<br/>"
        f"Please replace the 'start' and 'end' with a date yyyy-mm-dd anywhere between 2016-08-18 and 2017-08-18"
    )

@app.route("/api/v1.0/precipitation")    
def prcp():
    print("Server received request for 'prcp' page...")
    return jsonify(climate_dict)

@app.route("/api/v1.0/stations")    
def station():
    print("Server received request for 'station' page...")
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")    
def tobs():
    print("Server received request for 'tobs' page...")
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")    
def the_start(start):
    print("Server received request for 'start' page...")

    low_pre_join = [func.min(Measurement.tobs), Station.name]
    low_same_station = session.query(*low_pre_join).\
                filter(Measurement.station == Station.station).\
                filter(Measurement.date == start).all()
    high_pre_join = [func.max(Measurement.tobs), Station.name]
    high_same_station = session.query(*high_pre_join).\
                filter(Measurement.station == Station.station).\
                filter(Measurement.date == start).all()

    avg_pre_join = [func.avg(Measurement.tobs), Station.name]
    avg_same_station = session.query(*avg_pre_join).\
                filter(Measurement.station == Station.station).\
                filter(Measurement.date == start).all()

    if (low_same_station[0][0] == float and high_same_station[0][0] == float and avg_same_station[0][0] == float):
       start_dict = {
           "TMIN": low_same_station[0][0],
           "TAVG": avg_same_station[0][0],
           "TMAX": high_same_station[0][0]}
       return jsonify(start_dict)

    return jsonify({"error": f"The date {start} not found."}), 404

@app.route("/api/v1.0/<start>/<end>")    
def the_startend(start, end):
    print("Server received request for 'start-end' page...")
    low_pre_join = [func.min(Measurement.tobs), Station.name]
    low_same_station = session.query(*low_pre_join).\
                filter(Measurement.station == Station.station).\
                filter(Measurement.date >= start).\
                filter(Measurement.date <= end).all()
    high_pre_join = [func.max(Measurement.tobs), Station.name]
    high_same_station = session.query(*high_pre_join).\
                filter(Measurement.station == Station.station).\
                filter(Measurement.date >= start).\
                filter(Measurement.date <= end).all()

    avg_pre_join = [func.avg(Measurement.tobs), Station.name]
    avg_same_station = session.query(*avg_pre_join).\
                filter(Measurement.station == Station.station).\
                filter(Measurement.date >= start).\
                filter(Measurement.date <= end).all()

    if (low_same_station[0][0] == float and high_same_station[0][0] == float and avg_same_station[0][0] == float):
       start_end_dict = {
           "TMIN": low_same_station[0][0],
           "TAVG": avg_same_station[0][0],
           "TMAX": high_same_station[0][0]}
       return jsonify(start_end_dict)

    return jsonify({"error": f"The date {start} and {end} not found."}), 404



if __name__ == "__main__":
    app.run(debug=True)

    