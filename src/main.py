from mail import format_mail, send_email
from markdown import markdown
from notion_class import NotionUpdater
from requests_session import RateLimitedSession
from scrape import find_upcoming_projects

MAX_REQUESTS_PER_SECOND = 30
NOTION_MAX_REQUESTS_PER_SECOND = 3
TMDB_PERSON_URL = "https://www.themoviedb.org/person"
IMDB_PERSON_URL = "https://imdb.com/name"

def main():

    with RateLimitedSession(max_requests=MAX_REQUESTS_PER_SECOND) as tmdb_session:
        with RateLimitedSession(max_requests=NOTION_MAX_REQUESTS_PER_SECOND) as notion_session:
            
            notion_updater = NotionUpdater(session=notion_session)

            # TODO: Remove projects that have been released
            # Scrape new upcoming projects from all persons
            for person in notion_updater.person_list:
                projects = find_upcoming_projects(requests_session=tmdb_session, person=person)
                new_projects = []
                for project in projects:
                    if project.tmdb_id in person.projects:
                        continue
                    new_projects.append(project)
                    person.projects.append(project.tmdb_id)

                notion_updater.add_upcoming_projects_to_database(projects=new_projects)


    # mail_content_markdown = format_mail(project_organizer=project_organizer)
    # mail_content_html = markdown(mail_content_markdown)

    # subject = "Roundup of Upcoming Movies and TV Shows"
    # send_email(subject=subject, content=mail_content_html)
    

if __name__ == "__main__":
    import time
    start = time.time()
    main()
    stop = time.time()
    print(f"Done in {round(stop-start, 2)} s")