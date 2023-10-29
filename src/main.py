from custom_logger import CustomLogger
from notion_api_calls import NotionUpdater
from requests_session import RateLimitedSession
from tmdb_api_calls import find_upcoming_projects, get_released_projects_from_previous

import time

TMDB_MAX_REQUESTS_PER_SECOND = 30
NOTION_MAX_REQUESTS_PER_SECOND = 3


def get_excluded_projects():
    """Returns a list of tmdb_ids for projects that should not be added to the database"""
    with open("data/excluded_projects.txt", "r") as f:
        excluded_projects = f.read().splitlines()
    return excluded_projects


def main():

    with RateLimitedSession(max_requests=TMDB_MAX_REQUESTS_PER_SECOND) as tmdb_session:
        with RateLimitedSession(max_requests=NOTION_MAX_REQUESTS_PER_SECOND) as notion_session:
            
            notion_updater = NotionUpdater(session=notion_session)

            previous_projects = notion_updater.upcoming_list
            previous_project_tmdb_ids = [project.tmdb_id for project in previous_projects]
            CustomLogger.debug(f"Found {len(previous_projects)} projects in the UpcomingProjects database")

            # Remove projects where the Exclude checkbox has been checked from the databases
            notion_updater.remove_excluded_projects_from_databases()
            
            # Move projects that have been released to the ReleasedProjects database
            if previous_projects:
                released_projects = get_released_projects_from_previous(requests_session=tmdb_session, previous_projects=previous_projects)
                notion_updater.add_film_projects_to_database(projects=released_projects, database="released")
                notion_updater.remove_film_projects_from_database(projects=released_projects)

                CustomLogger.info(f"Moved {len(released_projects)} projects to the ReleasedProjects database")
                CustomLogger.info(f"Projects that have been moved from `UpcomingProjects` to `ReleasedProjects`: {released_projects}")


            new_projects = []
            excluded_projects = get_excluded_projects()

            # Scrape new upcoming projects from all persons
            for person in notion_updater.person_list:
                
                projects = find_upcoming_projects(requests_session=tmdb_session, person=person)

                for project in projects:
                    # Check if project is already in the database
                    if project.tmdb_id in previous_project_tmdb_ids:
                        CustomLogger.debug(f"Project '{project.title}' is already in the database")
                        continue

                    # Check if project is excluded
                    if project.tmdb_id in excluded_projects:
                        CustomLogger.debug(f"Project '{project.title}' is excluded from the database")
                        continue

                    # Check if the project is already in another person's list
                    used_tmdb_ids = [project.tmdb_id for project in new_projects]
                    if project.tmdb_id in used_tmdb_ids:

                        # Update the project with the new person
                        used_project = new_projects[used_tmdb_ids.index(project.tmdb_id)]
                        used_project.associated_person_page_ids.append(person.notion_page_id)
                        person.projects.append(project.tmdb_id)
                        
                        CustomLogger.debug(f"Project '{project.title}' already in another person's list. Updated associated people: {used_project.associated_person_page_ids}")
                        continue

                    new_projects.append(project)
                    person.projects.append(project.tmdb_id)
                
                CustomLogger.info(f"Found {len(projects)} upcoming projects for {person.name}")

            CustomLogger.debug(f"Adding new projects to the UpcomingProjects database")
            notion_updater.add_film_projects_to_database(projects=new_projects, database="upcoming")

    notion_updater.close()
    

if __name__ == "__main__":
    start = time.time()
    CustomLogger.info("Starting script")

    main()
    
    stop = time.time()
    CustomLogger.info(f"Finished script in {round(stop-start, 2)} s")