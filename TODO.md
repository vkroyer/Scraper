# TODO

- Add support for TV shows
- Include more details for each upcoming project
  - [Keywords](https://developer.themoviedb.org/reference/movie-keywords)
- [Include picture](https://developers.notion.com/reference/file-object) from TMDb of director/actor beside their name in the Notion database
- [Include picture](https://developers.notion.com/reference/file-object) from TMDb of movie poster in the Notion database
- Make a bash script or something that runs the python script e.g. every week on a Raspberry Pi

## Bugs/Issues/Stuff

- Figure out if the close method of NotionUpdater is necessary
  - Maybe the relations between Notion page ids and tmdb ids is not longer needed after all the code changes?
  - Would need to figure out if the script looks through the pages in the Notion database to ensure that upcoming projects already found at a previous time are not added to the database again
