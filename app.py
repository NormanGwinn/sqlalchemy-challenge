"""
## Step 2 - Climate App
"""

import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy.sql import label
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes['station']
Measurement = Base.classes['measurement']

# Most active station
most_active_station = 'USC00519281'
yr_ago = '2016-08-18'

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

def YearBefore(YYYY_MM_DD):
    return str(int(YYYY_MM_DD[0:4])-1) + YYYY_MM_DD[4:10]

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start date&gt;<br/>"
        f"/api/v1.0/&lt;start date&gt;/&lt;end date&gt;<br/>"
        f"<i>where dates are YYYY-MM-DD</i>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of dates and precipitation for the most active station"""
    # Query precipitation
    results = session.query(Measurement.date,Measurement.prcp).filter(Measurement.station == most_active_station).all()

    session.close()

    # Create a dictionary from the row data and append to a list of observations
    precipitation = []
    for date, prcp in results:
        dict = {}
        dict["date"] = date
        dict["prcp"] = prcp
        precipitation.append(dict)

    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations"""
    # Query all stations
    results = session.query(Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of dates and temperature for the most active station, for the last year of data"""
    # Query temperatures
    results = session.query(Measurement.date,Measurement.tobs)\
                     .filter(Measurement.station == most_active_station, Measurement.date > yr_ago)\
                     .all()

    session.close()

    # Create a dictionary from the row data and append to a list of observations
    list_tobs = []
    for date, tobs in results:
        dict = {}
        dict["date"] = date
        dict["tobs"] = tobs
        list_tobs.append(dict)

    return jsonify(list_tobs)

@app.route("/api/v1.0/<start>")
def start(start):
  # Create our session (link) from Python to the DB
  session = Session(engine)  

  # Calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
  results = session.query(
    label('station_name', Station.name), 
    label('min_temp', func.min(Measurement.tobs)),
    label('avg_temp', func.avg(Measurement.tobs)),
    label('max_temp', func.max(Measurement.tobs)),
    label('count', func.count(Measurement.tobs))
    ).group_by(Station.name).filter(Station.station == Measurement.station, Measurement.date >= f'{start}')

  session.close()

  # Create a dictionary from the row data and append to a list of observations
  list_station = []
  for station_name, min_tobs, avg_tobs, max_tobs, count in results:
      dict = {}
      dict["station_name"] = station_name
      dict["min_tobs"] = min_tobs
      dict["avg_tobs"] = avg_tobs
      dict["max_tobs"] = max_tobs
      dict["count_tobs"] = count
      list_station.append(dict)

  return jsonify(list_station)

@app.route("/api/v1.0/<start>/<end>")
def start_and_end_date(start, end):
  # Create our session (link) from Python to the DB
  session = Session(engine)  

  # Calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
  results = session.query(
    label('station_name', Station.name), 
    label('min_temp', func.min(Measurement.tobs)),
    label('avg_temp', func.avg(Measurement.tobs)),
    label('max_temp', func.max(Measurement.tobs)),
    label('count', func.count(Measurement.tobs))
    ).group_by(Station.name).filter(Station.station == Measurement.station, Measurement.date >= f'{start}', Measurement.date <= f'{end}')

  session.close()

  # Create a dictionary from the row data and append to a list of observations
  list_station = []
  for station_name, min_tobs, avg_tobs, max_tobs, count in results:
      dict = {}
      dict["station_name"] = station_name
      dict["min_tobs"] = min_tobs
      dict["avg_tobs"] = avg_tobs
      dict["max_tobs"] = max_tobs
      dict["count_tobs"] = count
      list_station.append(dict)

  return jsonify(list_station)
  #return jsonify([{'start' : f"'{start}'",'end' : f"'{end}'"}])

if __name__ == '__main__':
    app.run(debug=True)
