import os
import requests
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from bs4 import BeautifulSoup

class IMDbUser:
    def __init__(self, session):
        self._session = session

        self.username = os.environ.get("IMDB_USERNAME")
        self.password = os.environ.get("IMDB_PASSWORD")

    def login(self):
        payload = {"email":self.username, "password":self.password}
        # payload = {"ap_email":self.username, "ap_password":self.password}
        # post = self._session.post(IMDB_LOGIN_URL, data=payload)


class UserPreferences:
    def __init__(self):
        self._directors = []
        self._directors_url_ready = []
        self._actors = []
        self._actors_url_ready = []

    def update_directorlist(self):
        """Checks the online notepad for the latest version of a list of directors and updates the internal list in the class"""

        directorlist_url = os.environ.get("DIRECTORLIST_URL")

        response = requests.get(directorlist_url)
        soup = BeautifulSoup(response.content, features="html.parser")

        # Find the textarea and append all directors to the list
        directors_string = soup.find("div", {"class":"plaintext"}).text
        for director in directors_string.split("\n"):
            if director != "":
                self._directors.append(director)
                self._directors_url_ready.append("+".join(director.split())) # "+" between the names is used in the imdb search url

    def get_directors(self):
        """Returns a list of director names"""
        return self._directors

    def get_directors_url_ready(self):
        """Returns a list of director names formatted the way they should be in the IMDb search url"""
        return self._directors_url_ready


    def update_actorlist(self):
        """Checks the online notepad for the latest version of a list of actors and updates the internal list in the class"""

        actorlist_url = os.environ.get("ACTORLIST_URL")

        response = requests.get(actorlist_url)
        soup = BeautifulSoup(response.content, features="html.parser")

        # Find the textarea and append all actors to the list
        actors_string = soup.find("div", {"class":"plaintext"}).text
        for actor in actors_string.split("\n"):
            if actor != "":
                self._actors.append(actor)
                self._actors_url_ready.append("+".join(actor.split())) # "+" between the names is used in the imdb search url

    def get_actors(self):
        """Returns a list of actor names"""
        return self._actors

    def get_actors_url_ready(self):
        """Returns a list of actor names formatted the way they should be in the IMDb search url"""
        return self._actors_url_ready




if __name__ == "__main__":
    user = UserPreferences()

    # user.update_actorlist()
    # print("Actors from aNotepad:")
    # [print(actor) for actor in user.get_actors()]
    