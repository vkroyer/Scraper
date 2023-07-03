import json
import os
import re
from projects import FilmProject, instantiate_person, Person
from requests_session import RateLimitedSession
from dotenv import load_dotenv, find_dotenv

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
NOTION_UPCOMING_MULTISELECT_FILENAME = "notion_multiselect_genres/upcoming_genre_tags.json"
NOTION_RELEASED_MULTISELECT_FILENAME = "notion_multiselect_genres/released_genre_tags.json"


class NotionUpdater():
    """Class employing functionality for reading from and writing to Notion databases."""

    def __init__(self, session: RateLimitedSession) -> None:
        self._session = session
        self._person_list: "list[Person]" = []
        self._name_list: "list[str]" = []
        self._upcoming_list = []
        self._released_list = []
        self._upcoming_multiselect_options = {}
        self._released_multiselect_options = {}

    @property
    def person_list(self):
        self.update_person_list()
        return self._person_list
    
    @property
    def upcoming_list(self):
        self.update_upcoming_list()
        return self._upcoming_list
    
    @property
    def released_list(self):
        self.update_released_list()
        return self._released_list
    
    @property
    def upcoming_multiselect_options(self):
        if self._upcoming_multiselect_options == {}:
            with open(NOTION_UPCOMING_MULTISELECT_FILENAME, "r") as f:
                self._upcoming_multiselect_options = json.load(f)
        return self._upcoming_multiselect_options
    
    @property
    def released_multiselect_options(self):
        if self._released_multiselect_options == {}:
            with open(NOTION_RELEASED_MULTISELECT_FILENAME, "r") as f:
                self._released_multiselect_options = json.load(f)
        return self._released_multiselect_options

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
        
        return results

    def write_json_to_file(self, data, filename: str = "data/notion_personlist_json.json"):
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

    def update_json_files(self):
        filenames = [f"data/notion_{name}_json.json" for name in ["personlist", "upcoming", "released"]]
        urls = [GET_PERSON_DATABASE_URL, GET_UPCOMING_DATABASE_URL, GET_RELEASED_DATABASE_URL]

        for filename, url in zip(filenames, urls):
            data = self.read_database(url=url)
            self.write_json_to_file(data=data, filename=filename)


    def update_person_list(self):
        """Get all persons from Notion database. Used later to ensure film projects from newly added people are found."""
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

            imdb_url = properties["IMDb URL"]["url"]
            tmdb_url = properties["TMDb URL"]["url"]

            # Get the ID from the IMDb url
            imdb_id_regex = r".*nm([0-9]+)$"
            imdb_id = re.sub(imdb_id_regex, r"\1", imdb_url)

            # Get the ID from the TMDb url
            tmdb_id_regex = r".*\/person\/(\d+)-.*"
            tmdb_id = re.sub(tmdb_id_regex, r"\1", tmdb_url)

            person = instantiate_person(
                notion_page_id=page_id,
                tmdb_id=tmdb_id,
                imdb_id=imdb_id,
                tmdb_url=tmdb_url,
                imdb_url=imdb_url,
                name=name,
                is_director=is_director,
                is_actor=is_actor
            )
            self._person_list.append(person)
            self._name_list.append(name)

    def update_upcoming_list(self):
        """Get all upcoming projects from Notion database."""
        ...

    def update_released_list(self):
        """Get all released projects from Notion database."""
        ...


    def add_persons_to_database(self, persons: "list[Person]"):
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
    

    def add_upcoming_projects_to_database(self, projects: "list[FilmProject]"):
        """Add an upcoming project to the database with a relation link to the person database."""


    def create_page_in_upcoming_database(self, data: dict):
        """Creates an entry in the Notion database for an upcoming project.
        
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


    def create_page_in_released_database(self, data: dict):
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
    

def main():
    with RateLimitedSession(max_requests=3) as session:
        notion_updater = NotionUpdater(session=session)
        # notion_updater.update_json_files()
        # notion_updater.update_person_list()
        print(notion_updater.upcoming_multiselect_options)


if __name__ == "__main__":
    main()