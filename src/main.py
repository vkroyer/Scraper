from mail import format_mail, send_email
from markdown import markdown
from notion_class import NotionUpdater
from projects import instantiate_person, ProjectOrganizer
from requests_session import RateLimitedSession
from scrape import get_person_id, get_external_id_person, normalize_string, find_upcoming_projects

MAX_REQUESTS_PER_SECOND = 30
TMDB_PERSON_URL = "https://www.themoviedb.org/person"
IMDB_PERSON_URL = "https://imdb.com/name"

def main():
    project_organizer = ProjectOrganizer()
    project_organizer.get_previous_persons()
    project_organizer.get_previous_projects()

    with RateLimitedSession(max_requests=MAX_REQUESTS_PER_SECOND) as session:
        notion_updater = NotionUpdater(session=session)
        notion_updater.update_person_list()

        # Add new persons to the project organizer
        for person in notion_updater.person_list:
            name = person.name
            if name in [p.name for p in project_organizer.persons]:
                continue
            project_organizer.add_person(person)

        # TODO: Remove projects that have been released
        # Scrape new upcoming projects from all persons
        for person in project_organizer.persons:
            projects = find_upcoming_projects(requests_session=session, person=person)
            new_projects = []
            for project in projects:
                if project.tmdb_id in person.projects:
                    continue
                new_projects.append(project)
                person.projects.append(project.tmdb_id)

            project_organizer.add_projects(projects=new_projects)

    project_organizer.update_json_files()

    mail_content_markdown = format_mail(project_organizer=project_organizer)
    mail_content_html = markdown(mail_content_markdown)

    subject = "Roundup of Upcoming Movies and TV Shows"
    send_email(subject=subject, content=mail_content_html)
    

if __name__ == "__main__":
    import time
    start = time.time()
    main()
    stop = time.time()
    print(f"Done in {round(stop-start, 2)} s")