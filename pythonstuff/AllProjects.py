import json

##### FILES #####
PROJECTS_JSON = "data/project_log.json"
URL_JSON = "data/url_log.json"

class ProjectOrganizer:

    def __init__(self):
        self._director_projects = {} # {"name1":{"titles":["title1","title2",...], "links":["link1","link2",...]}, "name2":...}
        self._actor_projects = {}    # {"name1":{"titles":["title1","title2",...], "links":["link1","link2",...]}, "name2":...}

    def set_director_projects(self, director:str, projects:dict):
        self._director_projects[director] = projects

    def set_actor_projects(self, actor:str, projects:dict):
        self._actor_projects[actor] = projects

    def get_director_projects(self):
        return self._director_projects

    def get_actor_projects(self):
        return self._actor_projects

    def update_links(self, directors, director_links, actors, actor_links):
        with open(URL_JSON, "r") as file:
            json_content = json.load(file)
        
        for director, link in zip(directors, director_links):
            if director not in json_content["Directors"]:
                json_content["Directors"][director] = link
        
        for actor, link in zip(actors, actor_links):
            if actor not in json_content["Actors"]:
                json_content["Actors"][actor] = link

        with open(URL_JSON, "w") as file:
            json.dump(json_content, URL_JSON, indent=4)

    def get_previous_links(self):
        with open(URL_JSON, "r") as file:
            json_content = json.load(file)
        
        directors_link_dict = json_content["Directors"]
        actors_link_dict = json_content["Actors"]
        return directors_link_dict, actors_link_dict
        
    def update_upcoming_projects(self):
        """
        Updates the json file containing all the upcoming projects with directors and actors.
        If a new upcoming project doesn't exist in the json file, it will be updated with this project.
        """

        with open(PROJECTS_JSON, "r") as json_file:
            json_content = json.load(json_file)
        
        # Update json content with new directors and new projects for existing directors
        for director, projects in self._director_projects.items():
            if director not in json_content["Directors"]:
                json_content["Directors"][director] = projects
            for title, link in zip(projects["titles"], projects["links"]):
                if link not in json_content["Directors"][director]["links"]:
                    json_content["Directors"][director]["titles"].append(title)
                    json_content["Directors"][director]["links"].append(link)

        # Update json content with new actors and new projects for existing actors
        for actor, projects in self._actor_projects.items():
            if actor not in json_content["Actors"]:
                json_content["Actors"][actor] = projects
            for title, link in zip(projects["titles"], projects["links"]):
                if link not in json_content["Actors"][actor]["links"]:
                    json_content["Actors"][actor]["titles"].append(title)
                    json_content["Actors"][actor]["links"].append(link)

        # Write the final content to the json file
        with open(PROJECTS_JSON, "w") as json_file:
            json.dump(json_content, json_file, indent=4)

    def check_previous_upcoming_projects(self):
        """
        Checks the json file to see if any of the new upcoming projects that has been found
        already exist in the json file. 
        """
        with open(PROJECTS_JSON, "r") as json_file:
            full_json = json.load(json_file)

        # Remove previously scraped director projects
        prev_dir_projects = full_json["Directors"]
        for director, projects in prev_dir_projects.items():
            for link in projects["links"]:
                if link in self._director_projects[director]["links"]:
                    project_idx = self._director_projects[director]["links"].index(link)
                    del self._director_projects[director]["titles"][project_idx] # removes the project from the list of titles
                    del self._director_projects[director]["links"][project_idx] # removes the project from the list of links

        # Remove previously scraped actor projects
        prev_act_projects = full_json["Actors"]
        for actor, projects in prev_act_projects.items():
            for link in projects["links"]:
                if link in self._actor_projects[actor]["links"]:
                    project_idx = self._actor_projects[actor]["links"].index(link)
                    del self._actor_projects[actor]["titles"][project_idx] # removes the project from the list of titles
                    del self._actor_projects[actor]["links"][project_idx] # removes the project from the list of links
