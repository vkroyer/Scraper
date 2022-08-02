import os
import requests
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from bs4 import BeautifulSoup

class IMDbUser:
    def __init__(self):
        self.username = os.environ.get("IMDB_USERNAME")
        self.password = os.environ.get("IMDB_PASSWORD")
        self._directors = []
        self._directors_url_ready = []

    def update_directorlist(self):
        directorlist_url = os.environ.get("ANOTEPAD_URL")

        response = requests.get(directorlist_url)
        soup = BeautifulSoup(response.content, features="html.parser")

        # Find the textarea and append all directors to the list
        directors_string = soup.find("div", {"class":"plaintext"}).text
        for director in directors_string.split("\n"):
            self._directors.append(director)
            self._directors_url_ready.append("+".join(director.split())) # "+" between the names is used in the imdb search url
    
    def get_directors(self):
        return self._directors

    def get_directors_url_ready(self):
        return self._directors_url_ready



if __name__ == "__main__":
    user = IMDbUser()
    