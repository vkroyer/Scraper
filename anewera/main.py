from projects import instantiate_person
from User import UserPreferences
from scrape import Scraper
import json
import requests

def main():
    all_projects = []
    people = []

    user = UserPreferences()
    user.update_actorlist()
    user.update_directorlist()

    with requests.Session() as session:
        scraper = Scraper(session=session)
        people += [instantiate_person(scraper=scraper, name=name, is_director=True, is_actor=False) for name in user.get_directors()]
        # people += [instantiate_person(scraper=scraper, name=name, is_director=False, is_actor=True) for name in user.get_actors()]
    
    json_content = json.dumps({person.name:person.__dict__ for person in people}, indent=4)
    with open("stuff.json", "w") as f:
        f.write(json_content)

    #     for person in people:
    #         projects = scraper.get_projects(person.url, person.director)
    #         person.projects = [project.id for project in projects]
    #         all_projects += projects
    # for project in all_projects:
    #     print(project)

if __name__ == "__main__":
    import time
    start = time.time()
    main()
    stop = time.time()
    print(f"Done in {round(stop-start, 2)} s")