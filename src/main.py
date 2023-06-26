from mail import format_mail, send_email
from markdown import markdown
from projects import instantiate_person, AllProjects
from requests_session import RateLimitedSession
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

    with RateLimitedSession(max_requests=30) as session:

        # Add new persons to the all_projects organizer
        for name in user.persons:
            if name in [person.name for person in all_projects.persons]:
                continue
            person_id = get_person_id(requests_session=session, name=name)
            person_url = f"{TMDB_PERSON_URL}/{person_id}-{normalize_string(name)}"
            if name in user.directors:
                person = instantiate_person(tmdb_id=person_id, url=person_url, name=name, is_director=True, is_actor=False)
            elif name in user.actors:
                person = instantiate_person(tmdb_id=person_id, url=person_url, name=name, is_director=False, is_actor=True)
            all_projects.add_person(person)

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