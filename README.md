# A python script that looks for upcoming movies

## What it does

This script uses the [TMDb API](https://developers.themoviedb.org/3/getting-started/introduction) to look for upcoming movies. It then adds them to a [Notion](https://www.notion.so/) database. There are three Notion databases that are used:

1. People
2. Upcoming movies
3. Released movies

The first database is for actors and directors, the second is for upcoming movies, and the third is for movies that have been released. The movie databases have relation links to the person database, and the person database has a backlink to the two movie databases.

Every time the script is run, it checks the upcoming movies database to see if any of the movies have been released. If they have, it moves them to the released movies database. Then it checks the people database and looks for upcoming movies that they are involved in. If it finds any, it adds them to the upcoming movies database.

## How to use it

### Requirements

- Python 3.8.10 or newer
- [Notion account](https://www.notion.so/signup)
- [TMDb account](https://www.themoviedb.org/signup)

### Setup

1. Clone this repository
1. Install the requirements with `pip install -r requirements.txt`
1. Duplicate the Notion template [here](https://illeagle.notion.site/Movies-TEMPLATE-2399e7054dde473cbaedd86b4b750007?pvs=4) with the "Duplicate" button in the top right corner
1. Create a new integration in Notion and get the integration token as explained in step 1 [here](https://developers.notion.com/docs/create-a-notion-integration#step-1-create-an-integration)
1. Share all three databases with the integration as explained in step 2 [here](https://developers.notion.com/docs/create-a-notion-integration#step-2-share-a-database-with-your-integration)
1. Create a new API key in TMDb as explained [here](https://developers.themoviedb.org/3/getting-started/introduction)
1. Rename the `sample.env` file to `.env` and fill in the required information
   - `NOTION_API_TOKEN` is the integration token from step 4 above
   - `TMDB_API_TOKEN` is the API Read Access Token from step 6 above
   - The Notion database IDs can be found by following step 3 [here](https://developers.notion.com/docs/create-a-notion-integration#step-3-save-the-database-id)

### Running the script

Before the script is run, the `PersonList` database in Notion needs to be filled with people. The script will then look for upcoming movies that they are involved in and add them to the `UpcomingMovies` database. When the movies are released, the script will move them to the `ReleasedMovies` database.

The script is found at `src/main.py`.
