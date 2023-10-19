import json
import os
import re

from dotenv import find_dotenv, load_dotenv

from custom_dataclasses import FilmProject, Person
from custom_logger import CustomLogger
from requests_session import RateLimitedSession
from tmdb_api_calls import get_person_id, get_external_id_person

load_dotenv(find_dotenv())

# ENVIRONMENT VARIABLES
NOTION_API_TOKEN = os.environ.get("NOTION_API_TOKEN")
PERSON_LIST_DATABASE_ID = os.environ.get("PERSON_LIST_DATABASE_ID")
UPCOMING_PROJECTS_DATABASE_ID = os.environ.get("UPCOMING_PROJECTS_DATABASE_ID")
RELEASED_PROJECTS_DATABASE_ID = os.environ.get("RELEASED_PROJECTS_DATABASE_ID")

# API ENDPOINTS
GET_PERSON_DATABASE_URL = f"https://api.notion.com/v1/databases/{PERSON_LIST_DATABASE_ID}/query"
GET_UPCOMING_DATABASE_URL = f"https://api.notion.com/v1/databases/{UPCOMING_PROJECTS_DATABASE_ID}/query"
GET_RELEASED_DATABASE_URL = f"https://api.notion.com/v1/databases/{RELEASED_PROJECTS_DATABASE_ID}/query"
CREATE_PAGE_URL = f"https://api.notion.com/v1/pages"

HEADERS = {
    "Authorization": NOTION_API_TOKEN,
    "accept": "application/json",
    "Notion-Version": "2022-06-28",
    "content-type": "application/json"
}

# FILENAMES
NOTION_MULTISELECT_GENRES_FILENAME = "notion_multiselect_genres/genre_tags.json"
PREVIOUS_PROJECTS_FILENAME = "data/previous_projects.json"


# URLs
IMDB_PERSON_URL = "https://imdb.com/name"
TMDB_PERSON_URL = "https://www.themoviedb.org/person"


class NotionUpdater():
    """Class employing functionality for reading from and writing to Notion databases."""

    def __init__(self, session: RateLimitedSession) -> None:
        self._session = session
        self._person_list: "list[Person]" = []
        self._name_list: "list[str]" = []
        self._upcoming_list: "list[FilmProject]" = []
        self._released_list: "list[FilmProject]" = []
        self._previous_projects: "dict[str, str]" = {}
        self._upcoming_multiselect_options: "dict[str, dict[str, str]]" = {}
        self._released_multiselect_options: "dict[str, dict[str, str]]" = {}

        # Find all relevant previous data
        self.update_person_list()
        self.update_upcoming_list()
        self.update_released_list()


    @property
    def person_list(self):
        """List of objects of the `Person` dataclass, containing all directors and actors/actresses."""
        if self._person_list == []:
            self.update_person_list()
        for person in self._person_list:
            person.projects = [self.previous_projects[p_id] for p_id in person.project_page_ids]
        return self._person_list
    
    @property
    def upcoming_list(self):
        """List of objects of the `FilmProject` dataclass, containing all upcoming film projects."""
        if self._upcoming_list == []:
            self.update_upcoming_list()
        return self._upcoming_list
    
    @property
    def released_list(self):
        """List of objects of the `FilmProject` dataclass, containing all released film projects."""
        if self._released_list == []:
            self.update_released_list()
        return self._released_list
    
    @property
    def previous_projects(self):
        if self._previous_projects == {}:
            try:
                with open(PREVIOUS_PROJECTS_FILENAME, "r") as f:
                    self._previous_projects = json.load(f)
            except FileNotFoundError:
                # Make sure there is a file to read from in the future
                self.write_json_to_file(data={}, filename=PREVIOUS_PROJECTS_FILENAME)
        return self._previous_projects
    
    @property
    def multiselect_genre_options(self):
        """Dictionary containing all the json info about each genre tag in the databases in Notion."""
        if self._upcoming_multiselect_options == {}:
            with open(NOTION_MULTISELECT_GENRES_FILENAME, "r") as f:
                self._upcoming_multiselect_options = json.load(f)
        return self._upcoming_multiselect_options

    def read_database(self, url: str = GET_PERSON_DATABASE_URL):
        """Return all pages in a Notion database located at `url`."""
        payload = { "page_size": 100 }
        response = self._session.post(url, json=payload, headers=HEADERS)
        data = response.json()

        results = data["results"]

        while data["has_more"]:
            payload = {"page_size": 100, "start_cursor": data["next_cursor"]}
            response = self._session.post(url, json=payload, headers=HEADERS)
            data = response.json()
            results.extend(data["results"])

        CustomLogger.debug(f"Finished reading database at {url=}")
        
        return results

    def write_json_to_file(self, data, filename: str = "data/notion_personlist_json.json"):
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

    def update_json_files(self):
        """Dumps the json response for each notion database into a json file for easy viewing of response structure."""

        filenames = [f"data/notion_{name}_json.json" for name in ["personlist", "upcoming", "released"]]
        urls = [GET_PERSON_DATABASE_URL, GET_UPCOMING_DATABASE_URL, GET_RELEASED_DATABASE_URL]

        for filename, url in zip(filenames, urls):
            data = self.read_database(url=url)
            self.write_json_to_file(data=data, filename=filename)


    def update_person_list(self):
        """Get all persons from Notion database with their associated attributes."""
        results = self.read_database(url=GET_PERSON_DATABASE_URL)
        for result in results:
            page_id = result["id"]

            properties = result["properties"]

            name = properties["Name"]["title"][0]["plain_text"]

            is_director, is_actor = False, False
            for tag in properties["Tags"]["multi_select"]:
                if tag["name"] == "Director":
                    is_director = True
                elif tag["name"] == "Actor":
                    is_actor = True

            if not properties["IMDb URL"]["url"] or not properties["TMDb URL"]["url"]:

                CustomLogger.debug(f"Either IMDb url, TMDb url, or both urls are missing for {name}")

                # Find the IMDb and TMDb urls from the name
                tmdb_id = get_person_id(requests_session=self._session, name=name)
                tmdb_url = f"{TMDB_PERSON_URL}/{tmdb_id}"
                imdb_id = get_external_id_person(requests_session=self._session, person_id=tmdb_id)
                imdb_url = f"{IMDB_PERSON_URL}/{imdb_id}"

                # Add the urls to the person's page in the database
                url_payload = {
                    "properties": {
                        "IMDb URL": {"url": imdb_url},
                        "TMDb URL": {"url": tmdb_url}
                    }
                }
                response = self._session.patch(f"{CREATE_PAGE_URL}/{page_id}", headers=HEADERS, json=url_payload)

                CustomLogger.debug(f"Updated the page for {name} with their urls. Patch request response status code: {response.status_code}")

            else:
                imdb_url = properties["IMDb URL"]["url"]
                tmdb_url = properties["TMDb URL"]["url"]

            # Get the ID from the TMDb url
            tmdb_id_regex = r".*\/person\/(\d+)-.*"
            tmdb_id = re.sub(tmdb_id_regex, r"\1", tmdb_url)

            project_page_ids = [relation["id"] for relation in properties["Upcoming projects"]["relation"]]

            person = Person(
                notion_page_id=page_id,
                tmdb_id=tmdb_id,
                tmdb_url=tmdb_url,
                imdb_url=imdb_url,
                name=name,
                is_director=is_director,
                is_actor=is_actor
            )

            person.project_page_ids = project_page_ids

            if self.previous_projects:
                try:
                    person.projects = [self.previous_projects[page_id] for page_id in person.project_page_ids]
                except KeyError:
                    CustomLogger.warning(f"KeyError: {page_id} not found in previous projects")

            self._person_list.append(person)
            self._name_list.append(name)

    def get_projects(self, url: str) -> "list[FilmProject]":
        """Method for getting all `FilmProject`s of the database at `url`."""
        projects = []
        results = self.read_database(url=url)
        for result in results:
            project_page_id = result["id"]
            properties = result["properties"]
            
            person_page_ids = [relation["id"] for relation in properties["Included people"]["relation"]]

            title = properties["Title"]["title"][0]["text"]["content"]

            imdb_url = properties["IMDb URL"]["url"]
            tmdb_url = properties["TMDb URL"]["url"]

            # Get the ID from the TMDb url
            tmdb_id_regex = r".*\/movie\/(\d+)-.*"
            tmdb_id = re.sub(tmdb_id_regex, r"\1", tmdb_url)

            genres = [tag["name"] for tag in properties["Genres"]["multi_select"]]

            synopsis = properties["Synopsis"]["rich_text"][0]["text"]["content"]

            popularity = properties["Popularity"]["number"]

            if properties["Release date"]["date"]:
                release_date = properties["Release date"]["date"]["start"]
            else:
                release_date = None

            film_project = FilmProject(
                tmdb_id=tmdb_id,
                tmdb_url=tmdb_url,
                imdb_url=imdb_url,
                title=title,
                synopsis=synopsis,
                genres=genres,
                popularity=popularity,
                associated_person_page_ids=person_page_ids,
            )

            film_project.notion_page_id = project_page_id
            
            if release_date:
                film_project.release_date = release_date

            projects.append(film_project)

            if url == GET_UPCOMING_DATABASE_URL:
                self._previous_projects[project_page_id] = tmdb_id
        
        return projects

    def update_upcoming_list(self):
        """Get all upcoming projects from Notion database."""
        self._upcoming_list = self.get_projects(url=GET_UPCOMING_DATABASE_URL)

    def update_released_list(self):
        """Get all released projects from Notion database."""
        self._released_list = self.get_projects(url=GET_RELEASED_DATABASE_URL)


    def add_persons_to_database(self, persons: "list[Person]"):
        responses = []
        for person in persons:
            # Don't add person that's already in the Notion database
            if person.name in self._name_list:
                continue

            if person.is_director and not person.is_actor:
                tag = [{"id": "e89ad1f4-1d07-4918-932a-01ba3ad00ac0", "name": "Director", "color": "green"}]
            elif not person.is_director and person.is_actor:
                tag = [{'id': 'b758d37a-dfba-4038-9773-3cf384878e7e', 'name': 'Actor', 'color': 'blue'}]
            elif person.is_director and person.is_actor:
                tag = [
                    {"id": "e89ad1f4-1d07-4918-932a-01ba3ad00ac0", "name": "Director", "color": "green"},
                    {'id': 'b758d37a-dfba-4038-9773-3cf384878e7e', 'name': 'Actor', 'color': 'blue'}
                ]
            else:
                tag = []
            
            data = {
                "Name": {"title": [{"text": {"content": person.name}}]},
                "Tags": {"multi_select": tag},
                "IMDb URL": {"url": person.imdb_url},
                "TMDb URL": {"url": person.tmdb_url}
            }

            response = self.create_page_in_person_database(data=data)
            responses.append(response)
        
        return responses
        

    def create_page_in_person_database(self, data: dict):
        """Creates an entry in the Notion database for directors/actors.
        
        data must follow the format:
            data = {
                "Name": {"title": [{"text": {"content": <insert name>}}]},
                "Tags": {"multi_select": [<tag>]},
                "IMDb URL": {"url": <insert url>},
                "TMDb URL": {"url": <insert url>}
            }

            where tag is a list of either one or both of the following:
                {"id": "e89ad1f4-1d07-4918-932a-01ba3ad00ac0", "name": "Director", "color": "green"},
                {'id': 'b758d37a-dfba-4038-9773-3cf384878e7e', 'name': 'Actor', 'color': 'blue'}
        """

        url = CREATE_PAGE_URL
        payload = {"parent": {"database_id": PERSON_LIST_DATABASE_ID}, "properties": data}
        response = self._session.post(url, headers=HEADERS, json=payload)
        return response
    

    def add_film_projects_to_database(self, projects: "list[FilmProject]", database: str):
        """Add film projects to the database with a relation link to the person database.
        
        Param `database` must be either "upcoming" or "released".
        """

        if database == "upcoming":
            database_id = UPCOMING_PROJECTS_DATABASE_ID
        elif database == "released":
            database_id = RELEASED_PROJECTS_DATABASE_ID
        else:
            error = "Param `database` must be either 'upcoming' or 'released'."
            CustomLogger.error(error)
            raise ValueError(error)
        
        responses = []
        for project in projects:
            release_date = {"start": project.release_date} if hasattr(project, "release_date") else None
            data = {
                "Title": {"title": [{"text": {"content": project.title}}]},
                "Included people": {"relation": [{"id": p_id} for p_id in project.associated_person_page_ids]},
                "Genres": {"multi_select": [
                    self.multiselect_genre_options[genre] for genre in project.genres
                ]},
                "Synopsis": {"rich_text": [{"text": {"content": project.synopsis}}]},
                "IMDb URL": {"url": project.imdb_url if project.imdb_url else None},
                "TMDb URL": {"url": project.tmdb_url},
                "Popularity": {"number": project.popularity},
                "Release date": {"date": release_date}
            }
            response = self.create_page_in_database(data=data, database_id=database_id)
            responses.append(response)

            if response.status_code != 200:
                CustomLogger.warning(f"Something went wrong when adding {project.title} to the database. Response status code: {response.status_code}.")

        return responses
    
    def create_page_in_database(self, data: dict, database_id: str):
        """Creates an entry in the Notion database for a project.
        
        data must follow the format:
            data = {
                "Title": {"title": [{"text": {"content": <insert title>}}]},
                "Included people": {"relation": [{"id": <insert person page id>}]},
                "Genres": {"multi_select": <tags>},
                "Synopsis": {"rich_text": [{"text": {"content": <insert synopsis>}}]},
                "IMDb URL": {"url": <insert url>},
                "TMDb URL": {"url": <insert url>},
                "Popularity": {"number": <insert popularity>},
                "Release date": {"date": {"start": <insert date>}}
            }
            where tags is a list of genre multi_select options in json form.
        """
        url = CREATE_PAGE_URL
        payload = {"parent": {"database_id": database_id}, "properties": data}
        response = self._session.post(url, headers=HEADERS, json=payload)
        return response
    

    def remove_film_projects_from_database(self, projects: "list[FilmProject]"):
        """Remove film projects from the database."""
        
        responses = []
        for project in projects:
            response = self.delete_page(page_id=project.notion_page_id)
            responses.append(response)

            if response.status_code != 200:
                CustomLogger.warning(f"Something went wrong when deleting {project.title} from the database. Response status code: {response.status_code}.")
                
        
        return responses
    

    def delete_page(self, page_id: str):
        """Deletes a page from the Notion database."""
        url = f"{CREATE_PAGE_URL}/{page_id}"
        response = self._session.patch(url, headers=HEADERS, json={"archived": True})
        return response
    

    def close(self):
        """Save the relation between page ids and tmdb ids to a json file for future use."""
        
        # Update previous projects with new upcoming projects that have been found
        self._previous_projects = {project.notion_page_id: project.tmdb_id for project in self._upcoming_list}

        self.write_json_to_file(data=self._previous_projects, filename=PREVIOUS_PROJECTS_FILENAME)
    


if __name__ == "__main__":
    ...