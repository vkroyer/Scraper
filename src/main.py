import json
import requests
from mail import format_mail, send_email
from markdown import markdown
from projects import instantiate_person, AllProjects
from scrape import get_person_id, normalize_string, find_upcoming_projects
from user import UserPreferences

TMDB_PERSON_URL = "https://www.themoviedb.org/person"


def main():
    all_projects = AllProjects()
    all_projects.get_previous_persons()
    all_projects.get_previous_projects()

    user = UserPreferences()
    user.update_actorlist()
    user.update_directorlist()

    with requests.Session() as session:

        # TODO: Make director and actor functionality into the same if possible for tmdb

        # Add new directors to the all_projects organizer
        for director_name in user.directors:
            if director_name in [person.name for person in all_projects.directors]:
                continue
            person_id = get_person_id(requests_session=session, name=director_name)
            person_url = f"{TMDB_PERSON_URL}/{person_id}-{normalize_string(director_name)}"
            director = instantiate_person(tmdb_id=person_id, url=person_url, name=director_name, is_director=True, is_actor=False)
            all_projects.add_person(director)
        
        # Add new actors/actresses to the all_projects organizer
        for actor_name in user.actors:
            if actor_name in [person.name for person in all_projects.actors]:
                continue
            person_id = get_person_id(requests_session=session, name=actor_name)
            person_url = f"{TMDB_PERSON_URL}/{person_id}-{normalize_string(actor_name)}"
            actor = instantiate_person(tmdb_id=person_id, url=person_url, name=actor_name, is_director=False, is_actor=True)
            all_projects.add_person(actor)

        # TODO: Remove projects that have been released
        # Scrape new upcoming projects from all persons
        for person in all_projects.persons:
            projects = find_upcoming_projects(requests_session=session, person_id=person.tmdb_id)
            new_projects = []
            for project in projects:
                if project.tmdb_id in person.projects:
                    continue
                new_projects.append(project)
                person.projects.append(project.tmdb_id)

            all_projects.add_projects(projects=new_projects)

    all_projects.update_json_files()

    mail_content_markdown = format_mail(all_projects=all_projects)
    mail_content_html = markdown(mail_content_markdown)

    subject = "Roundup of Upcoming Movies and TV Shows"
    send_email(subject=subject, content=mail_content_html)
    

if __name__ == "__main__":
    import time
    start = time.time()
    main()
    stop = time.time()
    print(f"Done in {round(stop-start, 2)} s")