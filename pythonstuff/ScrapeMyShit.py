from bs4 import BeautifulSoup
import re

###################
#### CONSTANTS ####

#### URLs #########
IMDB_URL = "https://imdb.com"
IMDB_LOGIN_URL = "https://www.imdb.com/ap/signin"

## END CONSTANTS ##
###################

class Scraper:

    def __init__(self, session):
        self._session = session

    def get_peoples_links(self, names_url_ready:list):
        """Searches for the names in the list on IMDb and returns a list of links to their IMDb pages"""
        link_list = []
        for name in names_url_ready:
            response = self._session.post(f"{IMDB_URL}/find?q={name}&ref_=nv_sr_sm")
            soup = BeautifulSoup(response.text, features="html.parser")
            unique_link = soup.find("a", {"href":re.compile(r"/name/nm")})['href']

            name_link = f"{IMDB_URL}{unique_link}"
            link_list.append(name_link)

        return link_list

    def get_director_projects(self, director_url:str):
        project_dict = {"titles":[], "links":[]}

        directorpage = self._session.get(director_url)
        soup = BeautifulSoup(directorpage.text, "html.parser")

        director_element = soup.find("div", id="filmo-head-director")
        director_credits_element = director_element.find_next_sibling("div") # finds all the productions directed by the current director
        in_production_tags = director_credits_element.find_all("a", class_="in_production") # finds all productions that have not yet been released

        if not in_production_tags: # director has no upcoming projects :(
            return None

        for tag in in_production_tags:
            project_element = tag.find_parent("div")
            
            title = project_element.b.a.text
            link = project_element.b.a["href"]

            project_dict["titles"].append(title)
            project_dict["links"].append(link)
        
        return project_dict

    def get_actor_projects(self, actor_url:str):
        return None

    