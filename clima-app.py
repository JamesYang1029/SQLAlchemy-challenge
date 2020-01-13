import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})


Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

Measurements = Base.classes.measurement
Stations = Base.classes.station

session = Session(engine)

#weather app
app = Flask(__name__)


@app.route("/")
def home():
    return (f"Welcome to Surf's Up!: Hawai'i Climate API<br/>"
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~<br/>"
            f"Available Routes:<br/>"
            f"/api/v1.0/stations ~~~~~ a list of all weather observation stations<br/>"
            f"/api/v1.0/precipitaton ~~ the latest year of preceipitation data<br/>"
            f"/api/v1.0/tobs ~~ the latest year of temperature data<br/>"
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~<br/>"
            f"~~~ datesearch (yyyy-mm-dd)<br/>"
            f"/api/v1.0/datesearch/<startDate> ~~~~~~~~~~~ low, high, and average temp for date given and each date after<br/>"
            f"/api/v1.0/datesearch/<startDate>/<endDate> ~~ low, high, and average temp for date given and each date up to and including end date<br/>"
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~<br/>"
            f"~ data available from 2010-01-01 to 2017-08-23 ~<br/>"
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

@app.route("/api/v1.0/precipitation")
def precipitation():
    #Query for the dates and temperature observations from the last year.
    results = session.query(Measurements.date,Measurements.prcp).filter(Measurements.date >= "08-23-2017").all()
    year_prcp = list(np.ravel(results))
    return jsonify(year_prcp)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Stations.name).all()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def temperature():
    #Return a json list of Temperature Observations (tobs) for the previous year
    year_tobs = []
    results = session.query(Measurements.tobs).filter(Measurements.date >= "08-23-2017").all()
    year_tobs = list(np.ravel(results))
    return jsonify(year_tobs)

@app.route("/api/v1.0/datesearch/<startDate>")
def start(startDate):
    sel = [Measurements.date, func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurements.date) >= startDate)
                       .group_by(Measurements.date)
                       .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

@app.route("/api/v1.0/datesearch/<startDate>/<endDate>")
def startEnd(startDate, endDate):
    sel = [Measurements.date, func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurements.date) >= startDate)
                       .filter(func.strftime("%Y-%m-%d", Measurements.date) <= endDate)
                       .group_by(Measurements.date)
                       .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

if __name__ == "__main__":
    app.run(debug=True)