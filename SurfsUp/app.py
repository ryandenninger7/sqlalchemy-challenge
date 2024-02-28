from flask import Flask, jsonify
import datetime as dt

#Import from sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

#Flask App Creation
app = Flask(__name__)

#Engine creation and reflect databases
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
base = automap_base()
base.prepare(engine, reflect=True)

#References
measurement = base.classes.measurement
station = base.classes.station

#Session Creation
session = Session(engine)

#Routes
@app.route("/")
def home():
    """Routes available"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Results to dictionary to JSON output"""
    # Calculate the date one year ago from the most recent date
    most_recent_date = session.query(func.max(measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query precipitation data for the last 12 months
    results = session.query(measurement.date, measurement.prcp)\
                    .filter(measurement.date >= one_year_ago)\
                    .all()

    # Convert the query results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in results}

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations"""
    results = session.query(station.station).all()
    station_list = [station[0] for station in results]

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Query temperature observations for the most-active station and return as JSON"""
    most_active_station = session.query(measurement.station)\
                                    .group_by(measurement.station)\
                                    .order_by(func.count(measurement.station).desc())\
                                    .first()[0]

    results = session.query(measurement.date, measurement.tobs)\
                    .filter(measurement.station == most_active_station,
                            measurement.date >= one_year_ago)\
                    .all()

    tobs_list = [{"Date": date, "Temperature": tobs} for date, tobs in results]

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def temp_start(start):
    """Return JSON list of TMIN, TAVG, and TMAX for all dates greater than or equal to the start date"""
    results = session.query(func.min(measurement.tobs).label('TMIN'),
                            func.avg(measurement.tobs).label('TAVG'),
                            func.max(measurement.tobs).label('TMAX'))\
                    .filter(measurement.date >= start)\
                    .all()

    temp_data = [{"TMIN": result.TMIN, "TAVG": result.TAVG, "TMAX": result.TMAX} for result in results]

    return jsonify(temp_data)

@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):
    """Return JSON list of TMIN, TAVG, and TMAX for dates between start and end (inclusive)"""
    results = session.query(func.min(measurement.tobs).label('TMIN'),
                            func.avg(measurement.tobs).label('TAVG'),
                            func.max(measurement.tobs).label('TMAX'))\
                    .filter(measurement.date >= start, measurement.date <= end)\
                    .all()

    temp_data = [{"TMIN": result.TMIN, "TAVG": result.TAVG, "TMAX": result.TMAX} for result in results]

    return jsonify(temp_data)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)