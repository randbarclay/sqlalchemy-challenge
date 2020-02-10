import numpy as np
import datetime as dt
from datetime import datetime

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Base.metadata.tables # Check tables, not much useful
# Base.classes.keys() # Get the table names

Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation info: /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"Temperature for one year: /api/v1.0/tobs<br/>"
        f"Temperature info from given start date(must be yyyy-mm-dd format): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature info from given start to end date. Must be yyyy-mm-dd format: /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    session=Session(engine)
    results=session.query(Measurement.station,Measurement.date,Measurement.prcp).all()
    session.close()

    precipitation=[]
    for station,date,prcp in results:
        precipitation_dict={}
        precipitation_dict['station']=station
        precipitation_dict[f"{date}"]=prcp
        precipitation.append(precipitation_dict)

    return jsonify(precipitation)



@app.route('/api/v1.0/stations')
def stations():
    session=Session(engine)
    results=session.query(Station.station,Station.name).all()
    session.close()

    stations=[]
    for station, name in results:
        stations_dict={}
        stations_dict['Station ID']=station
        stations_dict['Station Name']=name
        stations.append(stations_dict)
    
    return jsonify(stations)

@app.route('/api/v1.0/tobs')
def tobs():
    session=Session(engine)
    last=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date=dt.datetime.strptime(last[0],"%Y-%m-%d")
    querydate = dt.date(last_date.year -1, last_date.month, last_date.day)
    
    results=session.query(Measurement.station,Measurement.date,Measurement.tobs).filter(Measurement.date>=querydate).all()
    session.close()

    tobs_info=[]
    for station, date, tobs in results:
        tobs_dict = {}
        tobs_dict["Station"] = station
        tobs_dict["Date"] = date
        tobs_dict["Precipitation"] = tobs
        tobs_info.append(tobs_dict)

    return jsonify(tobs_info)

#this is a nifty bit of work - this app will return the max/min/avg of every day given a yyyy-mm-dd
@app.route('/api/v1.0/<start>')
def start(start):
    session=Session(engine)
    #this will convert the 'start' from string to date
    st_date = datetime.strptime(start,"%Y-%m-%d")
    
    #here we are querying for the last date in the dataset
    max_date_query = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    #this will pull the date out and turn it into a string. since we only have one result from the above query, we don't need a for loop
    max_date = max_date_query[0]
    
    #converting the last date to a date format. if you're asking why this isn't redundant from the query result, it's because you can't reference that query result
    #in the same fashion. i *think* the query result is a tuple, but i'm not sure.
    last_date = datetime.strptime(max_date,"%Y-%m-%d")
    

    #empty set that we will fill and then jsonify
    statsforstart2 = []

    #this is our variable for the while loop. set it equal to the start date that the user inputs
    date_var = st_date

    #while loop. this will run as long as the variable date is less than or equal to the last date above.

    while date_var <= last_date:
        session=Session(engine)

        #query. we must change the format of the variable date to a string in order for the query to pull a successful result.

        results = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
            filter(Measurement.date == func.strftime("%Y-%m-%d",date_var)).all()
        
        #basic for loop that appends our data to each dict
        for date, min, max, avg in results:
            temp_range = {}
            temp_range["Date"] = date
            temp_range[f"Minimum on {date}"]=min
            temp_range[f"Maximum on {date}"]=max
            temp_range[f"Average on {date}"]=avg
            statsforstart2.append(temp_range)
        
        #adding 1 day to the date var at the end of our loop to ensure that the while condition will be broken
        date_var = date_var + dt.timedelta(days=1)


    return jsonify(statsforstart2)

#this app is basically the same as above, except we add a few variables for the 'stop' date
@app.route('/api/v1.0/<start>/<stop>')
def start_stop(start,stop):
    session=Session(engine)
    start_date = datetime.strptime(start,"%Y-%m-%d")
    stop_date = datetime.strptime(stop, "%Y-%m-%d")


    #empty set that we will fill and then jsonify
    statsforstart = []
    #set our variable date to our begin date
    date_var = start_date

    #while loop. this will run as long as the variable date is less than or equal to the last date above.
    while date_var <= stop_date:
        session=Session(engine)

        #query. we must change the format of the variable date to a string in order for the query to pull a successful result.
        results = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
            filter(Measurement.date == func.strftime("%Y-%m-%d",date_var)).all()
        
        #basic for loop that appends our data to each dict
        for date, min, max, avg in results:
            temp_range2 = {}
            temp_range2["Date"] = date
            temp_range2[f"Minimum on {date}"]=min
            temp_range2[f"Maximum on {date}"]=max
            temp_range2[f"Average on {date}"]=avg
            statsforstart.append(temp_range2)
        
        #adding 1 day to the date var at the end of our loop to ensure that the while condition will be broken
        date_var = date_var + dt.timedelta(days=1)


    return jsonify(statsforstart)


if __name__ == '__main__':
    app.run(debug=True)