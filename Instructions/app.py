from flask import Flask
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_

from flask import Flask, jsonify

app = Flask(__name__)

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

@app.route("/")
def welcome():
    return(f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;")

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    sel = [Measurement.date, Measurement.prcp]

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    #first_date = session.query(Measurement.date).order_by(Measurement.date).first()

    final_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    last_year = dt.date(final_date.year -1, final_date.month, final_date.day)
    results = session.query(*sel).filter(Measurement.date >= last_year).all()

    precip_date = []

    for prcp, date in results:
        precip_dict = {}
        precip_dict[date] = prcp
        precip_date.append(precip_dict)

    session.close()
    return jsonify(precip_date)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations = {}
    results = session.query(Station.station, Station.name).all()
    for s,name in results:
        stations[s] = name
    session.close()
 
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    sels = [Measurement.date, Measurement.tobs]
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    final_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    last_year = dt.date(final_date.year -1, final_date.month, final_date.day)
    results = session.query(*sels).filter(Measurement.date >= last_year).all()
    tobs_date = []

    for date, tobs in results:
        tob_dict = {}
        tob_dict[date] = tobs
        tobs_date.append(tob_dict)

    session.close()

    return jsonify(tobs_date)

@app.route("/api/v1.0/<start>")
def temp_start(start):
    session = Session(engine)
    start_list = []
    results = session.query(  Measurement.date, func.min(Measurement.tobs), \
                            func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start).group_by(Measurement.date).all()

    for date, min, avg, max in results:
        start_dict = {}
        start_dict["TMIN"] = min
        start_dict["Date"] = date
        start_dict["TAVG"] = avg
        start_dict["TMAX"] = max
        start_list.append(start_dict)

    session.close()    

    return jsonify(start_list)


@app.route("/api/v1.0/<start>/<end>")
def temp_range_start_end(start,end):
    session = Session(engine)

    end_list = []

    results = session.query(  Measurement.date, func.min(Measurement.tobs), \
                        func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                    filter(and_(Measurement.date >= start, Measurement.date <= end)). group_by(Measurement.date).all()

    for date, min, avg, max in results:
        end_dict = {}
        end_dict["TMIN"] = min
        end_dict["Date"] = date
        end_dict["TAVG"] = avg
        end_dict["TMAX"] = max
        end_list.append(end_dict)

    session.close()    
    return jsonify(end_list)

if __name__ == '__main__':
    app.run(debug=True)





    