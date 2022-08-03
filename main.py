import requests

from AllProjects import AllProjects
from ScrapeMyShit import Scraper
from SendEmail import send_email
from Users import UserPreferences

###################
#### CONSTANTS ####

#### URLs #########
IMDB_URL = "https://imdb.com"

## END CONSTANTS ##
###################

def get_upcoming_projects(all_projects):

    user_preferences = UserPreferences()
    user_preferences.update_directorlist()
    user_preferences.update_actorlist()

    directors = user_preferences.get_directors()
    actors = user_preferences.get_actors()

    directors_url_ready = user_preferences.get_directors_url_ready()
    actors_url_ready = user_preferences.get_actors_url_ready()

    with requests.Session() as session:
        scraper = Scraper(session)

        director_links = scraper.get_peoples_links(directors_url_ready)
        for director, dir_link in zip(directors, director_links):
            projects = scraper.get_director_projects(dir_link)
            if projects is not None:
                all_projects.set_director_projects(director, projects)
        
        actor_links = scraper.get_peoples_links(actors_url_ready)
        for actor, actor_link in zip(actors, actor_links):
            projects = scraper.get_actor_projects(actor_link)
            if projects is not None:
                all_projects.set_actor_projects(actor, projects)          


def format_one_upcoming_projects_list(name:str, title_list:list, link_list:list):
    sub_header = f"\n\n### {name.upper()} - Upcoming production(s)"
    projects_markdown = []
    for title, link in zip(title_list, link_list):
        projects_markdown.append(f"1. **{title}** ({IMDB_URL}{link})")
    body = "\n".join(projects_markdown)

    return f"{sub_header}\n{body}"


def format_mail(all_projects, director_flag:bool, actor_flag:bool):

    if not director_flag and not actor_flag:
        return None

    final_markdown_str = ""

    if director_flag:
        director_projects_header = "# A list of upcoming projects from directors I like in no particular order"
        director_projects_body = ""

        directors_projects = all_projects.get_director_projects()
        for director, projects in directors_projects.items():
            director_projects_body += format_one_upcoming_projects_list(director, projects["titles"], projects["links"])

        final_markdown_str += f"{director_projects_header}{director_projects_body}"

    if actor_flag:
        actor_projects_header = "\n\n\n# A list of upcoming projects from actors I like in no particular order"
        actor_projects_body = ""

        actors_projects = all_projects.get_actor_projects()
        for actor, projects in actors_projects.items():
            actor_projects_body += format_one_upcoming_projects_list(actor, projects["titles"], projects["links"])
    
        final_markdown_str += f"{actor_projects_header}{actor_projects_body}"
    
    return final_markdown_str


if __name__ == "__main__":

    all_projects = AllProjects()

    get_upcoming_projects(all_projects)
    mail_str = format_mail(all_projects, director_flag=True, actor_flag=False)

    subject = "Weekly roundup of upcoming projects in movies and television"
    to_address = "encodedspear@outlook.com"

    send_email(subject=subject, to_address=to_address, content=mail_str)

