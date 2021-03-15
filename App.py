#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 00:18:40 2021

@author: tiffanyelle
"""

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base #automatically generates mapped classes and relationships from a database schema
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify
import numpy as np
import datetime

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///"+"hawaii.sqlite")

# reflect an existing database into a new model
inspector = inspect(engine)
# reflect the tables
inspector.get_table_names()

# View all of the classes that automap found
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2017-07-10<br/>"
        f"/api/v1.0/2017-07-10/2018-08-18"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a dict of all date and temperature"""
    
    results = session.query(Measurement.date,Measurement.tobs).all()
    results_dict = {}
    for i,j in results:
        results_dict[i] = j

    session.close()

    return jsonify(results_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    results = session.query(Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))
    
    session.close()

    return jsonify(all_names)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    '''getting the most active station id'''
    result = session.query(Station.name,Station.station,func.count(Station.id)).\
        join(Measurement, Measurement.station==Station.station).\
        group_by(Station.name, Station.station).\
        order_by(func.count(Station.id).desc()).all()
    
    most_active_station = result[0][1]
    

    """Return a list of all stations"""
    start_date = datetime.date(2016, 1, 1)
    end_date = datetime.date(2017, 1, 1)
    res = session.query(Measurement.tobs).\
        filter(Measurement.station==most_active_station,Measurement.date>=start_date,Measurement.date<end_date).all()


    session.close()

    # Convert list of tuples into normal list
    all_tobs = list(set(list(np.ravel(res))))
    
    session.close()

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def start_date_records(start):
    print("------------------Start Date-----------------------------------------",start)
    session = Session(engine)
    res = session.query(Measurement.date,func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
            filter(Measurement.date>=start).\
            group_by(Measurement.date).all()
            
    session.close()
    
    d1 = {}
    d2 = {}

    for j in res:
        d1['TMIN'] = j[1]
        d1['TAVG'] = j[3]
        d1['TMAX'] = j[2]
        d2[j[0]] = d1
    
    return jsonify(d2)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date_records(start,end):
    print("--------------------Start Date---------------------------------------",start)
    print("--------------------End Date---------------------------------------",end)
    session = Session(engine)
    res = session.query(Measurement.date,func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
            filter(Measurement.date>=start,Measurement.date<=end).\
            group_by(Measurement.date).all()

    d1 = {}
    d2 = {}
    
    session.close()
    
    for j in res:
        d1['TMIN'] = j[1]
        d1['TAVG'] = j[3]
        d1['TMAX'] = j[2]
        d2[j[0]] = d1
    
    return jsonify(d2)


if __name__ == '__main__':
    app.run()