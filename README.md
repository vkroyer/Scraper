
# A little project that checks for upcoming movies and TV shows by certain directors

## The list of directors
An online notepad is used so the list of directors I like can be changed at any time from anywhere. The python script will then retrieve this list when it is run.

## IMDb
The script will go through the list of directors and look for their page on IMDb and search for movies and TV shows currently in production. All upcoming productions are listed in markdown format and written to a file.

## TODO
- Add same kind of functionality for actors I like
- Check some sort of website for news about these upcoming projects and add the news articles to a file or something
- Make a bash script or something that runs the python script e.g. every week
    - Maybe only include movies and TV shows that have not been included in a previous announcement
- Make the markdown file into an email that can be sent to me every time there are some new projects
- Include news articles and make it sort of like a newsletter