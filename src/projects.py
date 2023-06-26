import json
import random
import string
from dataclasses import asdict, dataclass, field

@dataclass
class FilmProject:
    tmdb_id: str
    url: str
    title: str
    synopsis: str
    genres: "list[str]" = field(default_factory=list)
    # director: str
    # stars: "list[str]" = field(default_factory=list)

    @property
    def __dict__(self):
        return asdict(self)
    
    @property
    def json(self):
        return json.dumps(self.__dict__, indent=4)


@dataclass
class Person:
    tmdb_id: str
    url: str
    name: str
    is_director: bool
    is_actor: bool
    projects: "list[str]" = field(default_factory=list) # list of FilmProject ids

    @property
    def __dict__(self):
        return asdict(self)

    @property
    def json(self):
        return json.dumps(self.__dict__)


def instantiate_person(tmdb_id:str, url:str, name:str, is_director:bool, is_actor:bool) -> Person:
    """Create an instance of a person from the id and name and is_(director/actor)."""
    person = Person(tmdb_id=tmdb_id, url=url, name=name, is_director=is_director, is_actor=is_actor)
    return person

def instansiate_previous_person(json_info:dict) -> Person:
    """Create an instance of a person with previously found info about the person."""
    person = Person(
        tmdb_id=json_info["id"],
        url=json_info["url"],
        name=json_info["name"],
        is_director=json_info["is_director"],
        is_actor=json_info["is_actor"]
    )

    person.projects = json_info["projects"]

    return person

def instansiate_previous_film_project(json_info:dict) -> FilmProject:
    """Create an instance of a film project with previously found info about the film project."""
    film_project = FilmProject(
        tmdb_id=json_info["id"],
        url=json_info["url"],
        title=json_info["title"],
        synopsis=json_info["synopsis"],
        genres=json_info["genres"]
    )

    return film_project

class AllProjects:
    """Class for containing all instances of dataclasses FilmProject and Person"""

    def __init__(self):
        self._film_projects: "list[FilmProject]" = []
        self._persons: "list[Person]" = []
        self._directors: "list[Person]" = []
        self._actors: "list[Person]" = []

    @property
    def film_projects(self):
        return self._film_projects

    @property
    def persons(self):
        return self._persons
    
    @property
    def directors(self):
        self.update_lists()
        return self._directors
    
    @property
    def actors(self):
        self.update_lists()
        return self._actors

    def add_projects(self, projects:"list[FilmProject]"):
        for project in projects:
            self._film_projects.append(project)

    def add_person(self, person:Person):
        self._persons.append(person)
        self._directors.append(person) if person.is_director else self._actors.append(person)

    def update_lists(self):
        """Updates list of actors and directors based on list of persons"""
        for person in self._persons:
            if person.is_director and person not in self._directors:
                self._directors.append(person)
            elif not person.is_director and person not in self._actors:
                self._actors.append(person)

    def get_previous_persons(self, filename_persons:str="data/person_log.json"):
        """Retrieve previously scraped information about directors/actors."""
        try:
            with open(filename_persons, "r") as f:
                person_dict = json.load(f)
                for person_info in person_dict.values():
                    person = instansiate_previous_person(json_info=person_info)
                    self.add_person(person)

        except FileNotFoundError as e:
            print(e)

    def get_previous_projects(self, filename_projects:str="data/film_project_log.json"):
        """Retrieve previously scraped information about upcoming projects."""
        try:
            with open(filename_projects, "r") as f:
                project_dict = json.load(f)
                film_projects = []
                for project_info in project_dict.values():
                    project = instansiate_previous_film_project(json_info=project_info)
                    film_projects.append(project)
                    
                self.add_projects(film_projects)

        except FileNotFoundError as e:
            print(e)


    def update_json_files(self):
        """Store all info about directors, actors/actresses and film projects in json files for later use."""
        person_json_content = json.dumps({person.name:person.__dict__ for person in self.persons}, indent=4)
        film_project_json_content = json.dumps({project.tmdb_id:project.__dict__ for project in self.film_projects}, indent=4)

        with open("data/person_log.json", "w") as f:
            f.write(person_json_content)

        with open("data/film_project_log.json", "w") as f:
            f.write(film_project_json_content)


if __name__ == "__main__":
    projs = AllProjects()
    projs.get_previous_persons()
    projs.get_previous_projects()