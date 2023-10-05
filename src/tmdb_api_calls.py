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

TMDB_API_MOVIE_DETAILS_URL = "https://api.themoviedb.org/3/movie"
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



def create_film_projects_from_response(requests_session: RateLimitedSession, json_data: dict, person: Person) -> "list[FilmProject]":
    """Extract relevant details from the API response and create `FilmProject` objects."""
    projects = []
    
    film_projects = json_data["results"]
    for film_project in film_projects:

        # Filter only projects that doesn't have a release date or that has a release date in the future
        release_date = film_project.get("release_date")
        if not release_date or datetime.strptime(release_date, "%Y-%m-%d").date() > DATE_TODAY:
        
            film_id = str(film_project["id"])

            # Fetch detailed information for the movie
            movie_credits_url = f"{TMDB_API_MOVIE_DETAILS_URL}/{film_id}/credits"
            response = requests_session.get(movie_credits_url, params={"language": "en-US"}, headers=HEADERS)
            movie_details = response.json()

            cast = movie_details.get("cast", [])
            crew = movie_details.get("crew", [])
            
            # Check if the person is in the cast or is the director
            person_found = False
            for cast_member in cast:
                if str(cast_member["id"]) == person.tmdb_id:
                    person_found = True
                    break
            if not person_found:
                for crew_member in crew:
                    crew_member_id = str(crew_member["id"])
                    crew_member_job = crew_member["job"]
                    if crew_member_id == person.tmdb_id and crew_member_job == "Director":
                        person_found = True
                        break
            if not person_found:
                continue

            title = film_project["title"]
            synopsis = film_project["overview"]
            genre_ids = film_project["genre_ids"]
            popularity = film_project["popularity"]

            imdb_id = get_external_id_project(requests_session=requests_session, project_id=film_id)
            imdb_url = f"{IMDB_MOVIE_URL}/{imdb_id}" if imdb_id else ""
            
            # Build the url for the film project
            normalized_title = normalize_string(title=title)
            tmdb_url = f"{TMDB_MOVIE_URL}/{film_id}-{normalized_title}"

            # Convert genre ids to actual genres
            genres = get_genres_by_id(requests_session=requests_session, genre_ids=genre_ids)
            project = FilmProject(
                tmdb_id=film_id,
                tmdb_url=tmdb_url,
                imdb_url=imdb_url,
                title=title,
                synopsis=synopsis,
                genres=genres,
                popularity=popularity,
                associated_person_page_ids=[person.notion_page_id],
            )

            if release_date:
                project.release_date = release_date

            projects.append(project)

    return projects


def find_upcoming_projects(requests_session: RateLimitedSession, person: Person) -> "list[FilmProject]":
    """Calls the API with the id of the person and returns upcoming projects with said person."""

    film_projects = []

    params = {
        "include_adult": False,
        "include_video": False,
        "language": "en-US",
        "sort_by": "primary_release_date.desc",
    }

    if person.is_actor:
        params["with_cast"] = person.tmdb_id

        response = requests_session.get(TMDB_API_MOVIES_URL, params=params, headers=HEADERS)

        data = response.json()

        if response.status_code == 200:
            projects = create_film_projects_from_response(requests_session=requests_session, json_data=data, person=person)
            film_projects.extend(projects)
        else:
            print(f"Error: {data['status_message']}")

    if person.is_director:
        params["with_crew"] = person.tmdb_id
        params["crew_position"] = "Director"

        response = requests_session.get(TMDB_API_MOVIES_URL, params=params, headers=HEADERS)

        data = response.json()

        if response.status_code == 200:
            projects = create_film_projects_from_response(requests_session=requests_session, json_data=data, person=person)
            film_projects.extend(projects)
        else:
            print(f"Error: {data['status_message']}")

    return film_projects


def get_released_projects_from_previous(requests_session: RateLimitedSession, previous_projects: "list[FilmProject]") -> "list[FilmProject]":
    """Check if any of the previous upcoming projects have been released and return the released projects."""

    released_projects: "list[FilmProject]" = []

    for project in previous_projects:
        movie_url = f"{TMDB_API_MOVIE_DETAILS_URL}/{project.tmdb_id}"
        response = requests_session.get(movie_url, params={"language": "en-US"}, headers=HEADERS)
        movie_details = response.json()

        if response.status_code == 200:
            release_date = movie_details.get("release_date")
            status = movie_details.get("status")
            if release_date and datetime.strptime(release_date, "%Y-%m-%d").date() < DATE_TODAY and status == "Released":
                released_projects.append(project)

    return released_projects


if __name__ == "__main__":
    ...
    with RateLimitedSession() as session:
        person = Person(
            notion_page_id="68d179cb-1e2d-4170-9809-adb732fdd836",
            tmdb_id="291263",
            tmdb_url="https://www.themoviedb.org/person/291263-jordan-peele",
            imdb_url="https://imdb.com/name/nm1443502",
            name="Jordan Peele",
            is_director=True,
            is_actor=False
        )
        projects = find_upcoming_projects(session, person)

        for project in projects:
            print(project.json)
