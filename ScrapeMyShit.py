import requests
from bs4 import BeautifulSoup
from user import IMDbUser
import re

###################
#### CONSTANTS ####

#### URLs #########
IMDB_URL = "https://imdb.com"
IMDB_LOGIN_URL = "https://www.imdb.com/ap/signin"

## END CONSTANTS ##
###################


if __name__ == "__main__":

    my_user = IMDbUser()
    my_user.update_directorlist()

    with requests.Session() as session:
        # payload = {"ap_email":my_user.username, "ap_password":my_user.password}
        # post = session.post(IMDB_LOGIN_URL, data=payload)

        director_list = my_user.get_directors()
        director_list_url_ready = my_user.get_directors_url_ready()
        director_url_list = []

        for i, director in enumerate(director_list_url_ready):
            con = session.post(f"https://www.imdb.com/find?q={director}&ref_=nv_sr_sm")
            soup = BeautifulSoup(con.text, features="html.parser")
            uniquelink = soup.find("a", {"href":re.compile(r"/name/nm")})['href']

            directorlink = f'{IMDB_URL}{uniquelink}'
            director_url_list.append(directorlink)

        total_announcement = ""
        for director, director_url in zip(director_list, director_url_list):

            directorpage = session.get(director_url)
            soup = BeautifulSoup(directorpage.text, "html.parser")

            director_element = soup.find("div", id="filmo-head-director")
            director_credits_element = director_element.find_next_sibling("div") # finds all the productions directed by the current director
            in_production_tags = director_credits_element.find_all("a", class_="in_production") # finds all productions that have not yet been released

            if not in_production_tags: # director has no upcoming projects :(
                continue

            header = f"\n\n# NEW PROJECTS IN PRODUCTION BY {director.upper()}:"
            total_announcement += header
            for tag in in_production_tags:
                project_element = tag.find_parent("div")
                
                title = project_element.b.a.text
                link = project_element.b.a["href"]

                total_announcement += f"\n1. **{title}** ({IMDB_URL}{link})"
        
        # Write the upcoming projects announcement to a markdown file
        with open("Announcement.md", "w") as f:
            f.write(total_announcement)
        
    