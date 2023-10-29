import json
from dataclasses import asdict, dataclass, field

@dataclass
class Person:
    notion_page_id: str
    tmdb_id: str
    tmdb_url: str
    imdb_url: str
    name: str
    is_director: bool
    is_actor: bool
    projects: "list[str]" = field(default_factory=list) # list of FilmProject ids
    project_page_ids: "list[str]" = field(default_factory=list) # list of Notion page ids for film projects

    @property
    def __dict__(self):
        return asdict(self)

    @property
    def json(self):
        return json.dumps(self.__dict__, indent=2)

@dataclass
class FilmProject:
    tmdb_id: str
    tmdb_url: str
    imdb_url: str
    title: str
    synopsis: str
    genres: "list[str]" = field(default_factory=list)
    popularity: float = 0.0
    associated_person_page_ids: "list[str]" = field(default_factory=list)
    release_date: str = field(init=False)
    notion_page_id: str = field(init=False)
    excluded: bool = field(init=False)

    @property
    def __dict__(self):
        if not hasattr(self, "release_date"):
            self.release_date = ""
        if not hasattr(self, "notion_page_id"):
            self.notion_page_id = ""
        return asdict(self)
    
    @property
    def json(self):
        return json.dumps(self.__dict__, indent=2)
