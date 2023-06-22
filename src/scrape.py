import json
import os
import re
import requests
from datetime import datetime
from dotenv import find_dotenv, load_dotenv
from projects import FilmProject, Person

load_dotenv(find_dotenv())

API_READ_ACCESS_TOKEN = os.environ.get("API_READ_ACCESS_TOKEN")
UPCOMING_MOVIES_URL = "https://api.themoviedb.org/3/discover/movie"
TMDB_MOVIE_URL = "https://www.themoviedb.org/movie"
TMDB_GENRES_URL = "https://api.themoviedb.org/3/genre/movie/list?language=en"
TMDB_GENRES_FILE = "data/genres.json"
DATE_TODAY = datetime.today().date()

HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {API_READ_ACCESS_TOKEN}"
}


def get_genres_by_id(genre_ids:"list[int]"):
    """Convert TMDb genre ids to the genre names, either from existing file or from the API."""

    all_genres: dict[str, str] = {}

    # Check if the genres file already exists
    if os.path.isfile(TMDB_GENRES_FILE):
        with open(TMDB_GENRES_FILE, "r") as file:
            all_genres = json.load(file)
    else:
        # Fetch the genres from the TMDB API
        response = requests.get(TMDB_GENRES_URL, headers=HEADERS)
        data = response.json()

        if response.status_code == 200:
            all_genres = {genre["id"]: genre["name"] for genre in data["genres"]}
            # Save the genres to a JSON file for future use
            with open(TMDB_GENRES_FILE, "w") as file:
                json.dump(all_genres, file)
        else:
            print(f"Error: {data['status_message']}")
    
    current_genres = [all_genres.get(str(genre_id)) for genre_id in genre_ids]
    current_genres = [genre for genre in current_genres if genre is not None]
    return current_genres


def normalize_title(title) -> str:
    # Remove or replace special characters
    normalized_title = re.sub(r"[^\w\s-]", "-", title)
    # Replace whitespace with dashes
    normalized_title = re.sub(r"\s+", "-", normalized_title)
    return normalized_title.lower()


def find_upcoming_projects(person_id) -> "list[FilmProject]":
    """Calls the API with the id of the person and returns upcoming projects with said person."""

    projects = []

    params = {
        "include_adult": False,
        "include_video": False,
        "language": "en-US",
        "sort_by": "popularity.desc",
        "with_crew": person_id
    }

    response = requests.get(UPCOMING_MOVIES_URL, params=params, headers=HEADERS)

    data = response.json()  # Parse the JSON response

    if response.status_code == 200:
        film_projects = data["results"]
        for film_project in film_projects:
            release_date = film_project.get("release_date")
            if not release_date or datetime.strptime(release_date, "%Y-%m-%d").date() > DATE_TODAY:
                title = film_project["title"]
                film_id = str(film_project["id"])
                synopsis = film_project["overview"]
                genre_ids = film_project["genre_ids"]
                
                # Build the url for the film project
                normalized_title = normalize_title(title=title)
                url = f"{TMDB_MOVIE_URL}/{film_id}-{normalized_title}"

                # Convert genre ids to actual genres
                genres = get_genres_by_id(genre_ids)

                projects.append(FilmProject(id=film_id, url=url, title=title, synopsis=synopsis, genres=genres))
    else:
        print(f"Error: {data['status_message']}")

    return projects


if __name__ == "__main__":
    guy_ritchie = "956"
    projects = find_upcoming_projects(guy_ritchie)

    for project in projects:
        print(project.json)