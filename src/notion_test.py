import json
import os
from projects import ProjectOrganizer
from requests_session import RateLimitedSession
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

NOTION_API_TOKEN = os.environ.get("NOTION_API_TOKEN")
PERSON_LIST_DATABASE_ID = os.environ.get("PERSON_LIST_DATABASE_ID")
UPCOMING_PROJECTS_DATABASE_ID = os.environ.get("UPCOMING_PROJECTS_DATABASE_ID")
RELEASED_PROJECTS_DATABASE_ID = os.environ.get("RELEASED_PROJECTS_DATABASE_ID")

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

def read_database(session: RateLimitedSession, url: str = GET_PERSON_DATABASE_URL):
    payload = { "page_size": 100 }
    response = session.post(url, json=payload, headers=HEADERS)

    data = response.json()

    with open("tests/notion_upcoming_json.json", "w") as f:
        json.dump(data, f)


def create_page_in_person_database(session: RateLimitedSession, data: dict):
    """Creates an entry in the Notion database for directors/actors.
    
    data must follow the format:
        data = {
            "Name": {"title": [{"text": {"content": <insert name>}}]},
            "Tags": {"multi_select": [<tag>]},
            "IMDb URL": {"url": <insert url>},
            "TMDb URL": {"url": <insert url>}
        }

        where tag is either one of or both of the following:
            {"id": "e89ad1f4-1d07-4918-932a-01ba3ad00ac0", "name": "Director", "color": "green"},
            {'id': 'b758d37a-dfba-4038-9773-3cf384878e7e', 'name': 'Actor', 'color': 'blue'}
    """

    url = CREATE_PAGE_URL
    payload = {"parent": {"database_id": PERSON_LIST_DATABASE_ID}, "properties": data}
    response = session.post(url, headers=HEADERS, json=payload)
    return response


def update_notion_persons():


def main():
    project_organizer = ProjectOrganizer()
    project_organizer.get_previous_persons()

    with RateLimitedSession(max_requests=3) as session:

        for person in project_organizer.persons:

            if person.is_director:
                tag = {"id": "e89ad1f4-1d07-4918-932a-01ba3ad00ac0", "name": "Director", "color": "green"}
            else:
                tag = {'id': 'b758d37a-dfba-4038-9773-3cf384878e7e', 'name': 'Actor', 'color': 'blue'}
            
            data = {
                "Name": {"title": [{"text": {"content": person.name}}]},
                "Tags": {"multi_select": [tag]},
                "IMDb URL": {"url": person.imdb_url},
                "TMDb URL": {"url": person.tmdb_url}
            }

            response = create_page_in_person_database(session=session, data=data)
            print(response.status_code)

main()