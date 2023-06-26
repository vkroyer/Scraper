import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class UserPreferences:
    def __init__(self):
        self._directors = []
        self._actors = []
        self._persons = []

    @property
    def directors(self):
        """Returns a list of director names."""
        return self._directors
    
    @property
    def actors(self):
        """Returns a list of actor names."""
        return self._actors
    
    @property
    def persons(self):
        """Returns a list of all director and actor names combined."""
        self._persons = self._actors + self._directors
        return self._persons

    def update_directorlist(self):
        """Checks the online notepad for the latest version of a list of directors and updates the internal list in the class."""

        directorlist_url = os.environ.get("DIRECTORLIST_URL")

        if not directorlist_url:
            return  # Early return if the directorlist_url is not defined

        response = requests.get(directorlist_url)
        if not response.ok:
            return  # Early return if the request was not successful

        # Parse html and find the text field with directors
        soup = BeautifulSoup(response.content, features="html.parser")
        plain_text_div = soup.find("div", {"class": "plaintext"})
        if not plain_text_div:
            return  # Early return if the plaintext div is not found

        directors_string = plain_text_div.text
        self._directors = [director for director in directors_string.split("\n") if director]

    def update_actorlist(self):
        """Checks the online notepad for the latest version of a list of actors and updates the internal list in the class."""

        actorlist_url = os.environ.get("ACTORLIST_URL")

        if not actorlist_url:
            return  # Early return if the actorlist_url is not defined

        response = requests.get(actorlist_url)
        if not response.ok:
            return  # Early return if the request was not successful

        # Parse html and find the text field with actors
        soup = BeautifulSoup(response.content, features="html.parser")
        plain_text_div = soup.find("div", {"class": "plaintext"})
        if not plain_text_div:
            return  # Early return if the plaintext div is not found

        actors_string = plain_text_div.text
        self._actors = [actor for actor in actors_string.split("\n") if actor]



if __name__ == "__main__":
    user = UserPreferences()

    user.update_actorlist()
    user.update_directorlist()
    print("\nActors from aNotepad:")
    [print(actor) for actor in user.actors]
    print("\nDirectors from aNotepad:")
    [print(director) for director in user.directors]
    