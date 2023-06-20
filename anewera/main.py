import json
import requests
from mail import format_mail, send_email
from markdown import markdown
from projects import instantiate_person, AllProjects
from scrape import Scraper
from user import UserPreferences

def main():
    all_projects = AllProjects()
    all_projects.get_previous_persons()
    all_projects.get_previous_projects()

    user = UserPreferences()
    user.update_actorlist()
    user.update_directorlist()

    with requests.Session() as session:
        scraper = Scraper(session=session)
        
        for director_name in user.directors:
            if director_name in [person.name for person in all_projects.directors]:
                continue
            director = instantiate_person(scraper=scraper, name=director_name, is_director=True, is_actor=False)
            all_projects.add_person(director)
        
        for actor_name in user.actors:
            if actor_name in [person.name for person in all_projects.actors]:
                continue
            actor = instantiate_person(scraper=scraper, name=actor_name, is_director=False, is_actor=True)
            all_projects.add_person(actor)

        for person in all_projects.persons:
            projects = scraper.get_projects(person)
            all_projects.add_projects(projects=projects)
            for project in projects:
                person.projects.append(project.id)


    person_json_content = json.dumps({person.name:person.__dict__ for person in all_projects.persons}, indent=4)
    film_project_json_content = json.dumps({project.id:project.__dict__ for project in all_projects.film_projects}, indent=4)

    with open("data/person_log.json", "w") as f:
        f.write(person_json_content)

    with open("data/film_project_log.json", "w") as f:
        f.write(film_project_json_content)


    

if __name__ == "__main__":
    import time
    start = time.time()
    main()
    stop = time.time()
    print(f"Done in {round(stop-start, 2)} s")