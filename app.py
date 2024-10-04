import icalendar
import requests
import pytz
from flask import Flask
from datetime import datetime
import pandas as pd


weather_url = "https://api.open-meteo.com/v1/forecast?latitude=60.1695&longitude=24.9354&hourly=temperature_2m,precipitation_probability,precipitation&forecast_days=16"
weather_response = requests.get(weather_url)

weather_data = weather_response.json()
weather_time_list = weather_data["hourly"]["time"]

# to datetime object
weather_time_list = [
    # datetime.strptime(time, "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc)
    datetime.strptime(time, "%Y-%m-%dT%H:%M").replace(tzinfo=pytz.UTC)
    for time in weather_time_list
]

weather_tempature_list = weather_data["hourly"]["temperature_2m"]
weather_rain_list = weather_data["hourly"]["precipitation_probability"]
weather_precipitation_probability = weather_data["hourly"]["precipitation"]

weather_data_zipped = list(
    zip(
        weather_time_list,
        weather_tempature_list,
        weather_rain_list,
        weather_precipitation_probability,
    )
)


calendar_url = "https://ics.tko-aly.fi/"

response = requests.get(calendar_url)

event_dict = {}

calendar = icalendar.Calendar.from_ical(response.content)

for event in calendar.walk("VEVENT"):
    event_name = str(event.decoded("SUMMARY"), "utf-8")
    gmt_eventdate = event.decoded("dtstart")
    pandas_event_date = pd.to_datetime(gmt_eventdate)
    rounded_event_date = pandas_event_date.floor("H").to_pydatetime()

    helsinki_time = gmt_eventdate + pd.Timedelta(hours=3)

    for i in weather_data_zipped:
        weather_date = i[0]
        if weather_date == rounded_event_date:
            event_dict[event_name] = [
                f"{str(helsinki_time)[:-9]} <br> <b>{round(i[1])} °C</b>  <br> sateen todennäköisyys: <b>{i[2]}%</b> <br> sademäärä: <b>{i[3]} mm</b>"
            ]


app = Flask(__name__)


@app.route("/")
def hello_world():
    html = "<h1>Tekis Weather</h1>"
    for event, weather in event_dict.items():
        html += f"<b><p>{event}</b>: <br> {weather[0]}</p>"
    html = (
        html
        + "<br><br><br><b>  </b> <br> <a href='https://www.cs.helsinki.fi/u/tonylam/'>Tony Lam</a>"
    )
    return html
