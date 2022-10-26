from bs4 import BeautifulSoup
from projects import FilmProject
import re

IMDB_URL = "https://imdb.com"


class Scraper:

    def __init__(self, session) -> None:
        self._session = session

    def get_IMDb_page_url(self, name_url_ready:str):
        """Searches for the name on IMDb and returns a link to their IMDb page"""

        response = self._session.post(f"{IMDB_URL}/find?q={name_url_ready}&ref_=nv_sr_sm")
        soup = BeautifulSoup(response.text, features="html.parser")
        unique_url = soup.find("a", {"href":re.compile(r"/name/nm")})['href']

        name_url = f"{IMDB_URL}{unique_url}"

        return name_url

    def get_projects(self, url:str, is_director:bool) -> "list[FilmProject]":
        """Looks for projects in production on an IMDb page and returns the projects"""

        projects = []

        page = self._session.get(url)
        soup = BeautifulSoup(page.text, "html.parser")

        if is_director:
            element = soup.find("div", id="filmo-head-director")
        elif not is_director:
            element = soup.find("div", id="filmo-head-actor")
            if element is None: element = soup.find("div", id="filmo-head-actress")

        credits_element = element.find_next_sibling("div") # finds all the productions directed by the current director
        in_production_tags = credits_element.find_all("a", class_="in_production") # finds all productions that have not yet been released

        if not in_production_tags: # no upcoming projects :(
            return []

        for tag in in_production_tags:
            if tag.text != "abandoned": # IMDb classifies abondoned productions with the same "in_production" html class smh..
                project_element = tag.find_parent("div")
                
                title = project_element.b.a.text
                project_url = f"{IMDB_URL}{project_element.b.a['href']}"
                # director = ""
                # synopsis = ""
                # genres = []
                # stars = []

                projects.append(
                    FilmProject(
                        url = project_url,
                        title = title,
                        # director = director,
                        # synopsis = synopsis,
                        # genres = genres,
                        # stars = stars
                    )
                )
        
        return projects