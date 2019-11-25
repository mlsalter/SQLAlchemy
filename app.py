import datetime as dt
import numpy as np
import pandas as pd

from flask import flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


#Setup Database

engine = create_engine("sqlite:///hawaii.sqlite")

#reflect an existing database into a new model
Base = automap_base()
#reflect the tables
Base.prepare(engine, reflect=True)

#Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station


#Setup Flask

#Create app name
app=Flask(__name__)

#Define all routes available
@app.route("/")
def welcome():
    return(
        f"Welcome to CAH or Climate Analysis - Hawaii API<br/>"
        f"Routes Available:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session(link) from Python to the DB
    session = Session(engine)

    """Return the precipitation data for the last_year"""
    #Calculate the date 1 year ago from the last data point in the database
    last_year = dt.date(2018, 8, 23) - dt.timedelta(days=365)

    # Query data and precipitation scores 
    prcp_last_yr = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_year).all()
 
    # Create a dictionary using date as the key and prcp as the value
    prcp_dict = {date: prcp for date,
                prcp in prcp_last_yr}

    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all passengers
    station_results = session.query(Station.station).all()
    session.close()

    # Inravel results and convert to a list
    stations_list = list(np.ravel(station_results))
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return the temperature observations (tobs) for last year"""
    # Calculate the date 1 year ago from last date in database
    last_year = dt.date(2018, 8, 23) - dt.timedelta(days=365)

    # Query tobs from the last year for the top station
    temp_last_yr = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= last_year).all()

    # Unravel results and convert to a list
    temp_list = list(np.ravel(results))

    return jsonify(temp_list)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return tmin, tavg, tmax"""
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # calculate tmin, tavg, tmax for dates greater than start
        results = session.query(*sel).filter(Measurement.date >= start).all()
        
        # Unravel results and convert to a list
        temps = list(np.ravel(results))
        return jsonify(temps)

    # calculate tmin, tavg, tmax with start and end
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    # Unravel results and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps)


if __name__ == '__main__':
    app.run()
