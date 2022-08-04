
class AllProjects:

    def __init__(self):
        self._director_projects = {}
        self._actor_projects = {}

    def set_director_projects(self, director:str, projects:dict):
        self._director_projects[director] = projects

    def set_actor_projects(self, actor:str, projects:dict):
        self._actor_projects[actor] = projects

    def get_director_projects(self):
        return self._director_projects

    def get_actor_projects(self):
        return self._actor_projects
        