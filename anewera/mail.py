import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv, find_dotenv
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


def format_one_upcoming_projects_list(name:str, title_list:list, link_list:list):
    """Returns a string with the name of the actor/director as a subheader and the projects with clickable titles in an ordered markdown list"""
    sub_header = f"\n\n### {name.upper()}"
    projects_markdown = []
    for title, link in zip(title_list, link_list):
        projects_markdown.append(f"1. **[{title}]({link})**")
    body = "\n".join(projects_markdown)

    return f"{sub_header}\n{body}"


def format_mail(project_organizer, director_flag=True, actor_flag=True):
    if not director_flag and not actor_flag:
        return ""

    final_markdown_str = ""

    if director_flag:
        director_projects_header = "# List(s) of upcoming projects from the directors you have chosen"
        director_projects_body = ""

        directors_projects = project_organizer.get_director_projects()
        for director, projects in directors_projects.items():
            if len(projects["links"]) > 0:
                director_projects_body += format_one_upcoming_projects_list(director, projects["titles"], projects["links"])
        
        if director_projects_body != "":
            final_markdown_str += f"{director_projects_header}{director_projects_body}"

    if actor_flag:
        actor_projects_header = "\n\n\n# List(s) of upcoming projects from the actors/actresses you have chosen"
        actor_projects_body = ""

        actors_projects = project_organizer.get_actor_projects()
        for actor, projects in actors_projects.items():
            if len(projects["links"]) > 0:
                actor_projects_body += format_one_upcoming_projects_list(actor, projects["titles"], projects["links"])
        
        if actor_projects_body != "":
            final_markdown_str += f"{actor_projects_header}{actor_projects_body}"
    
    if final_markdown_str == "":
        final_markdown_str = "## Shit is pre scraped...\nThere are no new upcoming projects from the directors/actors/actresses you have chosen since the last email update. **That sucks**"

    return final_markdown_str