import json
from dataclasses import asdict, dataclass, field

@dataclass
class Person:
    notion_page_id: str
    tmdb_id: str
    imdb_id: str
    tmdb_url: str
    imdb_url: str
    name: str
    is_director: bool
    is_actor: bool
    projects: "list[str]" = field(default_factory=list) # list of FilmProject ids

    @property
    def __dict__(self):
        return asdict(self)

    @property
    def json(self):
        return json.dumps(self.__dict__, indent=2)

@dataclass
class FilmProject:
    associated_person: Person
    tmdb_id: str
    imdb_id: str
    tmdb_url: str
    imdb_url: str
    title: str
    synopsis: str
    genres: "list[str]" = field(default_factory=list)

    # release_date: str = field(init=False)
    # director: str
    # stars: "list[str]" = field(default_factory=list)

    @property
    def __dict__(self):
        return asdict(self)
    
    @property
    def json(self):
        return json.dumps(self.__dict__, indent=2)


def instantiate_person(
        notion_page_id:str,
        tmdb_id:str,
        imdb_id:str,
        tmdb_url:str,
        imdb_url:str,
        name:str,
        is_director:bool,
        is_actor:bool) -> Person:
    """Create an instance of a person from the id and name and is_(director/actor)."""
    person = Person(
        notion_page_id=notion_page_id,
        tmdb_id=tmdb_id,
        imdb_id=imdb_id,
        tmdb_url=tmdb_url,
        imdb_url=imdb_url,
        name=name,
        is_director=is_director,
        is_actor=is_actor
    )
    return person

def instansiate_previous_person(json_info:dict) -> Person:
    """Create an instance of a person with previously found info about the person."""
    person = Person(
        notion_page_id=json_info["notion_page_id"],
        tmdb_id=json_info["tmdb_id"],
        imdb_id=json_info["imdb_id"],
        tmdb_url=json_info["tmdb_url"],
        imdb_url=json_info["imdb_url"],
        name=json_info["name"],
        is_director=json_info["is_director"],
        is_actor=json_info["is_actor"]
    )

    person.projects = json_info["projects"]

    return person

def instansiate_previous_film_project(json_info:dict) -> FilmProject:
    """Create an instance of a film project with previously found info about the film project."""
    film_project = FilmProject(
        associated_person=json_info["associated_person"],
        tmdb_id=json_info["tmdb_id"],
        imdb_id=json_info["imdb_id"],
        tmdb_url=json_info["tmdb_url"],
        imdb_url=json_info["imdb_url"],
        title=json_info["title"],
        synopsis=json_info["synopsis"],
        genres=json_info["genres"]
    )

    return film_project

class ProjectOrganizer:
    """Class for containing all instances of dataclasses FilmProject and Person"""

    def __init__(self):
        self._film_projects: "list[FilmProject]" = []
        self._persons: "list[Person]" = []

    @property
    def film_projects(self):
        return self._film_projects

    @property
    def persons(self):
        return self._persons

    def add_projects(self, projects: "list[FilmProject]"):
        for project in projects:
            self._film_projects.append(project)

    def add_person(self, person: Person):
        self._persons.append(person)


if __name__ == "__main__":
    ...
    projs = ProjectOrganizer()
