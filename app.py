import icalendar
import requests
from flask import Flask


weather_url = "https://api.open-meteo.com/v1/forecast?latitude=60.1695&longitude=24.9354&hourly=temperature_2m,precipitation_probability&forecast_days=16"
weather_response = requests.get(weather_url)

weather_data = weather_response.json()
weather_time_list = weather_data["hourly"]["time"]
weather_tempature_list = weather_data["hourly"]["temperature_2m"]
weather_rain_list = weather_data["hourly"]["precipitation_probability"]
weather_data_zipped = list(
    zip(weather_time_list, weather_tempature_list, weather_rain_list)
)

weather_time_list_fixed = []

for i in weather_data_zipped:
    day = i[0][:10]
    hour = i[0][11:14]
    weather_time_list_fixed.append(f"{day} {hour}")

weather_data_zipped_fixed = zip(
    weather_time_list_fixed, weather_tempature_list, weather_rain_list
)

calendar_url = "https://ics.tko-aly.fi/"

response = requests.get(calendar_url)

event_dict = {}

calendar = icalendar.Calendar.from_ical(response.content)
for event in calendar.walk("VEVENT"):
    name = str(event.decoded("SUMMARY"), "utf-8")
    date = str(event.decoded("dtstart"))

    for i in weather_data_zipped_fixed:
        if i[0] == date[:14]:
            event_dict[name] = [
                f"{date} on <b>{i[1]} celcius-astetta lämmintä</b> ja sateen todennäköisyys on <b>{i[2]}%</b>"
            ]
            break


app = Flask(__name__)


@app.route("/")
def hello_world():
    html = "<h1>Tekis Weather</h1>"
    for event, weather in event_dict.items():
        html += f"<p>{event}: <br> {weather[0]}</p>"
    return html
