from flask import Flask, render_template, request
from geopy.geocoders import Nominatim
from real_news_disaster_search import RealNewsDisasterSearch
import re

app = Flask(__name__)
searcher = RealNewsDisasterSearch()
geolocator = Nominatim(user_agent="disaster_app")

URL_PATTERN = re.compile(r'https?://\S+')

@app.route('/', methods=['GET', 'POST'])
def home():
    city_or_url = None
    incidents = []
    real_news = []
    ai_reports = []
    lat = lon = None
    error = None
    news_analysis = None
    incident_coords = []  # store lat/lon of incidents

    if request.method == 'POST':
        city_or_url = request.form.get('city_or_url')
        if not city_or_url:
            error = "Please enter a city name or news URL."
        else:
            try:
                if URL_PATTERN.match(city_or_url):
                    news_analysis = searcher.analyze_news_url(city_or_url)
                else:
                    data = searcher.search_city(city_or_url, return_data=True)
                    real_news = data.get("real_news", [])
                    ai_reports = data.get("ai_reports", [])
                    incidents = data.get("incidents", [])

                    # Geocode main city
                    location = geolocator.geocode(city_or_url)
                    if location:
                        lat, lon = location.latitude, location.longitude

                    # Geocode each incident if location exists
                    for inc in incidents:
                        try:
                            if inc.location:
                                loc = geolocator.geocode(inc.location)
                                if loc:
                                    incident_coords.append({
                                        "lat": loc.latitude,
                                        "lon": loc.longitude,
                                        "type": inc.need_type,
                                        "summary": inc.summary,
                                        "urgency": inc.urgency
                                    })
                        except:
                            pass
            except Exception as e:
                error = f"Error occurred: {str(e)}"

    return render_template(
        'index.html',
        city_or_url=city_or_url,
        incidents=incidents,
        real_news=real_news,
        ai_reports=ai_reports,
        lat=lat,
        lon=lon,
        error=error,
        news_analysis=news_analysis,
        incident_coords=incident_coords
    )

if __name__ == '__main__':
    app.run(debug=True)
