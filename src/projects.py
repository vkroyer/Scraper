import json
import random
import string
from dataclasses import asdict, dataclass, field

def generate_id() -> str:
    chars = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choices(chars, k=16))

@dataclass
class FilmProject:
    id: str = field(init=False, default_factory=generate_id)
    url: str
    title: str
    director: str
    # synopsis: str
    # genres: "list[str]" = field(default_factory=list)
    # stars: "list[str]" = field(default_factory=list)

    @property
    def __dict__(self):
        return asdict(self)

    @property
    def json(self):
        return json.dumps(self.__dict__)


@dataclass
class Person:
    id: str = field(init=False, default_factory=generate_id)
    name: str
    name_url_ready: str = field(init=False)
    url: str = field(init=False)
    is_director: bool
    is_actor: bool
    projects: "list[str]" = field(default_factory=list) # list of FilmProject ids

    def __post_init__(self):
        self.name_url_ready = "+".join(self.name.split()).lower()

    @property
    def __dict__(self):
        return asdict(self)

    @property
    def json(self):
        return json.dumps(self.__dict__)


def instantiate_person(scraper, name:str, is_director:bool, is_actor:bool) -> Person:
    """Create an instance of a person from just the name and is_(director/actor)."""
    person = Person(name=name, is_director=is_director, is_actor=is_actor)
    person.url = scraper.get_IMDb_page_url(name_url_ready=person.name_url_ready)
    return person

def instansiate_previous_person(json_info:dict) -> Person:
    """Create an instance of a person with previously found info about the person."""
    person = Person(
        name=json_info["name"],
        is_director=json_info["is_director"],
        is_actor=json_info["is_actor"]
    )

    person.id = json_info["id"]
    person.url = json_info["url"]
    person.projects = json_info["projects"]

    return person

def instansiate_previous_film_project(json_info:dict) -> FilmProject:
    """Create an instance of a film project with previously found info about the film project."""
    film_project = FilmProject(
        url=json_info["url"],
        title=json_info["title"],
        director=json_info["director"]
    )
    film_project.id = json_info["id"]

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



if __name__ == "__main__":
    projs = AllProjects()
    projs.get_previous_persons()
    projs.get_previous_projects()