import os
import smtplib
from dotenv import load_dotenv, find_dotenv
from email.message import EmailMessage
from projects import AllProjects, FilmProject, Person

load_dotenv(find_dotenv())

EMAIL_SENDER_ADDRESS = os.environ.get("EMAIL_SENDER_ADDRESS")
EMAIL_SENDER_PASSWORD = os.environ.get("EMAIL_SENDER_PASSWORD")
EMAIL_RECEIVER_ADDRESS = os.environ.get("EMAIL_RECEIVER_ADDRESS")

def send_email(subject:str, content:str, to_address:str=EMAIL_RECEIVER_ADDRESS):

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER_ADDRESS
    msg["To"] = to_address
    msg.set_content(content, subtype="html")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_SENDER_ADDRESS, EMAIL_SENDER_PASSWORD)
        smtp.send_message(msg)


def format_one_upcoming_projects_list(person: Person, projects:"list[FilmProject]"):
    """Returns a string with the name of the actor/director as a subheader and the projects with clickable titles in an ordered markdown list"""
    sub_header = f"\n\n### [{person.name.upper()}]({person.imdb_url})"
    projects_markdown = []
    for project in projects:
        with_genres = f" **{project.genres}**" if project.genres else "" # Add the list if genres if any exist
        with_synopsis = f": {project.synopsis}" if project.synopsis else "" # Add the plot description if it exists
        projects_markdown.append(f"1. **[{project.title}]({project.imdb_url})**{with_genres}{with_synopsis}")
    body = "\n".join(projects_markdown)

    return f"{sub_header}\n{body}"


def format_mail(all_projects:AllProjects, director_flag=True, actor_flag=True):
    if not director_flag and not actor_flag:
        return ""

    final_markdown_str = ""

    if director_flag:
        director_projects_header = "# List(s) of upcoming projects from the directors you have chosen"
        director_projects_body = ""

        for director in all_projects.directors:
            if len(director.projects) > 0:
                film_projects = [project for project in all_projects.film_projects if project.tmdb_id in director.projects]
                director_projects_body += format_one_upcoming_projects_list(director, film_projects)
        
        if director_projects_body != "":
            final_markdown_str += f"{director_projects_header}{director_projects_body}"

    if actor_flag:
        actor_projects_header = "\n\n\n# List(s) of upcoming projects from the actors/actresses you have chosen"
        actor_projects_body = ""

        for actor in all_projects.actors:
            if len(actor.projects) > 0:
                film_projects = [project for project in all_projects.film_projects if project.tmdb_id in actor.projects]
                actor_projects_body += format_one_upcoming_projects_list(actor, film_projects)
        
        if actor_projects_body != "":
            final_markdown_str += f"{actor_projects_header}{actor_projects_body}"
    
    if final_markdown_str == "":
        final_markdown_str = "## There are no new upcoming projects from the directors/actors/actresses you have chosen since the last email update."

    return final_markdown_str