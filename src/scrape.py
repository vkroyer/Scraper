import json
import os
import re
from datetime import datetime
from dotenv import find_dotenv, load_dotenv
from custom_dataclasses import FilmProject, Person
from requests_session import RateLimitedSession

load_dotenv(find_dotenv())


##### CONSTANTS #####

TMDB_API_TOKEN = os.environ.get("TMDB_API_TOKEN")

IMDB_MOVIE_URL = "https://imdb.com/title"

TMDB_MOVIE_URL = "https://www.themoviedb.org/movie"
TMDB_PERSON_URL = "https://www.themoviedb.org/person"

TMDB_API_MOVIES_URL = "https://api.themoviedb.org/3/discover/movie"
TMDB_API_PERSON_URL = "https://api.themoviedb.org/3/search/person?query="
TMDB_API_GENRES_URL = "https://api.themoviedb.org/3/genre/movie/list?language=en"
# TMDB_API_EXT_ID_URL = "https://api.themoviedb.org/3/movie/"

TMDB_GENRES_FILE = "data/genres.json"
TMDB_PERSON_IDS_FILE = "data/person_ids.json"

DATE_TODAY = datetime.today().date()

HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {TMDB_API_TOKEN}"
}



def normalize_string(title: str) -> str:
    """Normalizes a string to find the correct url version of the string."""

    # Remove or replace special characters
    normalized_title = re.sub(r"[^\w\s-]", "-", title)
    # Replace whitespace with dashes
    normalized_title = re.sub(r"\s+", "-", normalized_title)
    # Remove any excess dashes
    normalized_title = re.sub(r"-+", "-", normalized_title)
    # Remove any trailing dash
    normalized_title = normalized_title.rstrip("-")
    return normalized_title.lower()


def get_person_id(requests_session: RateLimitedSession, name: str) -> str:
    """Looks up the id of the director/actor on TMDb for use in future API calls with this person."""
    person_id = ""

    response = requests_session.get(f"{TMDB_API_PERSON_URL}{name}", headers=HEADERS)

    data = response.json()
    if response.status_code == 200 and data["results"]:
        person_id = data["results"][0]["id"]
        
    return person_id


def get_external_id_person(requests_session: RateLimitedSession, person_id: str) -> str:
    """Retrieve external (imdb) id for a person."""
    imdb_id = ""
    external_ids_url = f"https://api.themoviedb.org/3/person/{person_id}/external_ids"

    response = requests_session.get(external_ids_url, headers=HEADERS)

    data = response.json()
    if response.status_code == 200:
        imdb_id = data["imdb_id"]
    else:
        print(f"Error: {data['status_message']}")

    return imdb_id


def get_external_id_project(requests_session: RateLimitedSession, project_id: str) -> str:
    """Retrieve external (imdb) id for a film project."""
    imdb_id = ""
    external_ids_url = f"https://api.themoviedb.org/3/movie/{project_id}/external_ids"

    response = requests_session.get(external_ids_url, headers=HEADERS)

    data = response.json()
    if response.status_code == 200:
        imdb_id = data["imdb_id"]
    else:
        print(f"Error: {data['status_message']}")

    return imdb_id


def get_genres_by_id(requests_session: RateLimitedSession, genre_ids: "list[int]") -> "list[str]":
    """Convert TMDb genre ids to the genre names, either from existing file or from the API."""

    all_genres: dict[str, str] = {}

    # Check if the genres file already exists
    if os.path.isfile(TMDB_GENRES_FILE):
        with open(TMDB_GENRES_FILE, "r") as file:
            all_genres = json.load(file)
    else:
        # Fetch the genres from the TMDB API
        response = requests_session.get(TMDB_API_GENRES_URL, headers=HEADERS)
        data = response.json()

        if response.status_code == 200:
            all_genres = {genre["id"]: genre["name"] for genre in data["genres"]}
            
            # Save the genres to a JSON file for future use
            with open(TMDB_GENRES_FILE, "w") as file:
                json.dump(all_genres, file, indent=4)
        else:
            print(f"Error: {data['status_message']}")
    
    current_genres = [all_genres.get(str(genre_id)) for genre_id in genre_ids]
    current_genres = [genre for genre in current_genres if genre is not None]
    return current_genres


def find_upcoming_projects(requests_session: RateLimitedSession, person: Person) -> "list[FilmProject]":
    """Calls the API with the id of the person and returns upcoming projects with said person."""

    projects = []

    params = {
        "include_adult": False,
        "include_video": False,
        "language": "en-US",
        "sort_by": "primary_release_date.desc",
    }

    if person.is_actor:
        params["with_cast"] = person.tmdb_id
    elif person.is_director:
        params["with_crew"] = person.tmdb_id
        params["crew_position"] = "Director"

    response = requests_session.get(TMDB_API_MOVIES_URL, params=params, headers=HEADERS)

    data = response.json()

    if response.status_code == 200:
        film_projects = data["results"]
        for film_project in film_projects:
            # Filter only projects that doesn't have a release date or that has a release date in the future
            release_date = film_project.get("release_date")
            if not release_date or datetime.strptime(release_date, "%Y-%m-%d").date() > DATE_TODAY:
                title = film_project["title"]
                film_id = str(film_project["id"])
                synopsis = film_project["overview"]
                genre_ids = film_project["genre_ids"]

                imdb_id = get_external_id_project(requests_session=requests_session, project_id=film_id)
                imdb_url = f"{IMDB_MOVIE_URL}/{imdb_id}" if imdb_id else ""
                
                # Build the url for the film project
                normalized_title = normalize_string(title=title)
                tmdb_url = f"{TMDB_MOVIE_URL}/{film_id}-{normalized_title}"

                # Convert genre ids to actual genres
                genres = get_genres_by_id(requests_session=requests_session, genre_ids=genre_ids)
                project = FilmProject(
                    associated_person_page_id=person.notion_page_id,
                    tmdb_id=film_id,
                    tmdb_url=tmdb_url,
                    imdb_url=imdb_url,
                    title=title,
                    synopsis=synopsis,
                    genres=genres
                )
                projects.append(project)
    else:
        print(f"Error: {data['status_message']}")

    return projects


if __name__ == "__main__":
    ...
    # with RateLimitedSession() as session:
    #     person_id = get_person_id(session, "James Cameron")
    #     person = Person(person_id, "", "", "James Cameron", is_director=True, is_actor=False)
    #     projects = find_upcoming_projects(session, person)

    #     for project in projects:
            # print(project.json)
