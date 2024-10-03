import icalendar
import requests
from flask import Flask
from datetime import timedelta


weather_url = "https://api.open-meteo.com/v1/forecast?latitude=60.1695&longitude=24.9354&hourly=temperature_2m,precipitation_probability,precipitation&forecast_days=16"
weather_response = requests.get(weather_url)

weather_data = weather_response.json()
weather_time_list = weather_data["hourly"]["time"]
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

weather_time_list_fixed = []

for i in weather_data_zipped:
    day = i[0][:10]
    hour = i[0][11:14]
    weather_time_list_fixed.append(f"{day} {hour}")

weather_data_zipped_fixed = zip(
    weather_time_list_fixed,
    weather_tempature_list,
    weather_rain_list,
    weather_precipitation_probability,
)

for i in weather_data_zipped_fixed:
    print(i)

calendar_url = "https://ics.tko-aly.fi/"

response = requests.get(calendar_url)


# Function to round time to the nearest hour
def round_time_to_nearest_hour(dt):
    if dt.minute >= 30:
        dt = dt + timedelta(hours=1)
    return dt.replace(minute=0, second=0, microsecond=0)


event_dict = {}

calendar = icalendar.Calendar.from_ical(response.content)
for event in calendar.walk("VEVENT"):
    name = str(event.decoded("SUMMARY"), "utf-8")
    date = str(event.decoded("dtstart"))
    gmt_date = event.decoded("dtstart")

    for i in weather_data_zipped_fixed:
        weather_date_hour = i[0][:13]
        if weather_date_hour == date[:13]:
            event_dict[name] = [
                f"{str(gmt_date + timedelta(hours=3))[:-9]} <br> <b>{round(i[1])} °C</b>  <br> sateen todennäköisyys: <b>{i[2]}%</b> <br> sademäärä: <b>{i[3]} mm</b>"
            ]
            break

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
