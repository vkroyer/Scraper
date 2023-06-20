from bs4 import BeautifulSoup
from projects import FilmProject, Person
import re

IMDB_URL = "https://imdb.com"
REQUEST_HEADERS = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0"}

DIRECTOR_UPCOMING_CLASS_NAME = "ipc-metadata-list ipc-metadata-list--dividers-between date-unrel-credits-list ipc-metadata-list--base"



class Scraper:

    def __init__(self, session) -> None:
        self._session = session

    def get_IMDb_page_url(self, name_url_ready:str):
        """Searches for the name on IMDb and returns a link to their IMDb page"""

        url = f"{IMDB_URL}/find?q={name_url_ready}&ref_=nv_sr_sm"
        response = self._session.get(url, headers=REQUEST_HEADERS)
        soup = BeautifulSoup(response.text, features="html.parser")
        url_result = soup.find("a", {"href":re.compile(r"/name/nm")})
        if url_result:
            unique_url = url_result['href']
            name_url = f"{IMDB_URL}{unique_url}"
        else:
            name_url = ""

        return name_url

    def get_projects(self, person:Person) -> "list[FilmProject]":
        """Looks for projects in production on an IMDb page and returns the projects"""

        if person.url is None:
            return []

        projects = []

        page = self._session.get(person.url, headers=REQUEST_HEADERS)
        soup = BeautifulSoup(page.text, "html.parser")

        upcoming_list_element = None
        if person.is_director:
            try:
                # Find the elements in the html corresponding to the list of upcoming projects
                h3_element = soup.find("h3", text="Director")
                upcoming_element = h3_element.find_next("li", text="Upcoming")
                upcoming_list_element = upcoming_element.find_next("ul", class_=DIRECTOR_UPCOMING_CLASS_NAME)
            except AttributeError:
                print(f"Director credits not displayed by default for current director: {person.name}")
        
        if upcoming_list_element is None: # no upcoming projects :(
            return []

        for element in upcoming_list_element.contents:
            
            project_element = element.find_next("a", class_="ipc-metadata-list-summary-item__t")
            
            if not project_element:
                continue

            title = project_element.text
            project_url = f"{IMDB_URL}{project_element.attrs['href']}"
            director = ""
            if person.is_director:
                director = person.name
            # synopsis = ""
            # genres = []
            # stars = []

            film_project = FilmProject(url=project_url, title=title, director=director)

            projects.append(film_project)
    
        return projects