
# A little project that checks for upcoming movies and TV shows by certain directors (and actors maybe)

## The list of directors
An online notepad is used so the list of directors I like can be changed at any time from anywhere. The python script will then retrieve this list when it is run.

## IMDb
The script will go through the list of directors and look for their page on IMDb and search for movies and TV shows currently in production. 

## Output of Python code
All upcoming productions are listed in markdown format and written to a file. A preview of the format can be seen in [this file](https://github.com/vkroyer/Scraper/blob/master/OutputPreview.md).

## TODO
- Check some sort of website for news about these upcoming projects and add the news articles to a file or something
- Make a bash script or something that runs the python script e.g. every week on a Raspberry Pi
- Maybe only include movies and TV shows that have not been included in a previous announcement
    - Create a json file or something that is updated with all the new upcoming projects
    - Next time the script is run: Check if the json file already includes upcoming projects that has been found
    - Check if any of the upcoming projects in the json file has been released
- Convert the markdown string to html for a nicely formatted email
- Include news articles and make it sort of like a newsletter
