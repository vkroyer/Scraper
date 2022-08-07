from markdown import markdown
import requests

from pythonstuff.AllProjects import ProjectOrganizer
from pythonstuff.ScrapeMyShit import Scraper
from pythonstuff.SendEmail import send_email
from pythonstuff.Users import UserPreferences

def get_upcoming_projects(project_organizer):

    user_preferences = UserPreferences()
    user_preferences.update_directorlist()
    user_preferences.update_actorlist()

    directors = user_preferences.get_directors()
    actors = user_preferences.get_actors()

    directors_url_ready = user_preferences.get_directors_url_ready()
    actors_url_ready = user_preferences.get_actors_url_ready()

    # TODO: bruk denne jævelen som inneholder tidligere linker til imdb for å slippe å finne den samme linken hver gang programmet blir kjørt
    previous_directors_link_dict, previous_actors_link_dict = project_organizer.get_previous_links()

    with requests.Session() as session:
        scraper = Scraper(session)
        director_links = scraper.get_peoples_links(directors_url_ready)
        for director, dir_link in zip(directors, director_links):
            projects = scraper.get_director_projects(dir_link)
            if projects is not None:
                project_organizer.set_director_projects(director, projects)

        actor_links = scraper.get_peoples_links(actors_url_ready)
        for actor, actor_link in zip(actors, actor_links):
            projects = scraper.get_actor_projects(actor_link)
            if projects is not None:
                project_organizer.set_actor_projects(actor, projects)

    project_organizer.update_links(directors, director_links, actors, actor_links)


def format_one_upcoming_projects_list(name:str, title_list:list, link_list:list):
    """Returns a string with the name of the actor/director as a subheader and the projects with clickable titles in an ordered markdown list"""
    sub_header = f"\n\n### {name.upper()} - Upcoming production{'s' if len(title_list)>1 else ''}"
    projects_markdown = []
    for title, link in zip(title_list, link_list):
        projects_markdown.append(f"1. **[{title}]({link})**")
    body = "\n".join(projects_markdown)

    return f"{sub_header}\n{body}"


def format_mail(project_organizer, director_flag=True, actor_flag=True):
    if not director_flag and not actor_flag:
        return None

    final_markdown_str = ""

    if director_flag:
        director_projects_header = "# A list of upcoming projects from the directors you have chosen"
        director_projects_body = ""

        directors_projects = project_organizer.get_director_projects()
        for director, projects in directors_projects.items():
            if len(projects["links"]) > 0:
                director_projects_body += format_one_upcoming_projects_list(director, projects["titles"], projects["links"])
        
        if director_projects_body != "":
            final_markdown_str += f"{director_projects_header}{director_projects_body}"

    if actor_flag:
        actor_projects_header = "\n\n\n# A list of upcoming projects from the actors/actresses you have chosen"
        actor_projects_body = ""

        actors_projects = project_organizer.get_actor_projects()
        for actor, projects in actors_projects.items():
            if len(projects["links"]) > 0:
                actor_projects_body += format_one_upcoming_projects_list(actor, projects["titles"], projects["links"])
        
        if actor_projects_body != "":
            final_markdown_str += f"{actor_projects_header}{actor_projects_body}"
    
    if final_markdown_str == "":
        final_markdown_str = "There are no new upcoming projects from the directors/actors/actresses you have chosen since the last email update. That sucks"

    return final_markdown_str


if __name__ == "__main__":

    project_organizer = ProjectOrganizer()

    get_upcoming_projects(project_organizer)

    project_organizer.check_previous_upcoming_projects()
    project_organizer.update_upcoming_projects()

    mail_markdown = format_mail(project_organizer)
    mail_html = markdown(mail_markdown) # Converts markdown to html with the markdown module

    subject = "Roundup of upcoming movies and TV shows"

    send_email(subject=subject, content=mail_html)

    # For previewing what the mail content will look like
    with open("tests/markdown_mailcontent.md", "w") as f:
        f.write(mail_markdown)
    with open("tests/html_mailcontent.html", "w") as f:
        f.write(mail_html)

