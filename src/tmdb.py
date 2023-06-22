import os
import requests
from datetime import datetime
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

API_READ_ACCESS_TOKEN = os.environ.get("API_READ_ACCESS_TOKEN")
DIRECTOR_SEARCH_URL = "https://api.themoviedb.org/3/search/person"
UPCOMING_MOVIES_URL = "https://api.themoviedb.org/3/discover/movie"

DATE_TODAY = datetime.today().date()
DIRECTOR_ID = 956

HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {API_READ_ACCESS_TOKEN}"
}

params = {
    "include_adult": False,
    "include_video": False,
    "language": "en-US",
    "sort_by": "popularity.desc",
    "with_crew": DIRECTOR_ID  # Use the director's ID here
}

response = requests.get(UPCOMING_MOVIES_URL, params=params, headers=HEADERS)
data = response.json()  # Parse the JSON response

if response.status_code == 200:
    movies = data["results"]
    for movie in movies:
        title = movie["title"]
        release_date = movie.get("release_date", default="")
        if not release_date or datetime.strptime(release_date, "%Y-%m-%d").date() > DATE_TODAY:
            print(f"Title: {title}, Release Date: {release_date}")
else:
    print(f"Error: {data['status_message']}")
