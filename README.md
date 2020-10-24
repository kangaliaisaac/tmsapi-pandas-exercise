### Movie Showings Docs
https://developer.tmsapi.com/docs/read/data_v1_1/movies/Movies_playing_in_local_theatres


### Movie Airings on TV
https://developer.tmsapi.com/docs/read/data_v1_1/movies/Movies_on_TV_by_day


### Playground: 
https://developer.tmsapi.com/io-docs


# Setting Up

## Pre-requisites
- [Python 3](https://www.python.org/)
- [MySQL](https://dev.mysql.com/) - Follow the docs to set up your DB and DB User
 
## Instructions

* Clone repo
* `cd` into the root directory and activate virtualenv

    ```bash
    $ cd /path/to/root/directory/
    $ python3 -m virtualenv venv
    $ . venv/bin/activate
    $ . .env
    ```
  
    In your ``.env`` file export the following variables
    
    ```bash
    #! /usr/bin/bash

    export API_SECRET=""
    export DB_USER=""
    export DB_PASS=""
    export DB_NAME=""

    ```
 
* Install requirements

    ```bash
    $ pip install --upgrade pip
    $ pip install -r requirements.txt
    ```

# Testing

* Launch ipython

    ```bash
    $ ipython
    Python 3.8.1 (v3.8.1:1b293b6006, Dec 18 2019, 14:08:53)
    Type 'copyright', 'credits' or 'license' for more information
    IPython 7.18.1 -- An enhanced Interactive Python. Type '?' for help.
    
    In [1]:
    ```
  
* To fetch data for Showings and save in the `theatre_movies` DB table:
 
    ```bash
    ...
    In [1]: import tmsapi
  
    In [2]: tmsapi.fetch_data_from_api(data_for="SHOWINGS", zip_code="78701", start_date="2020-10-24")
    ```
  
* To fetch data for TV Airings and save in the `tv_movies` DB table:
 
    ```bash
    ...
    In [1]: import tmsapi
  
    In [2]: tmsapi.fetch_data_from_api(data_for="AIRINGS", lineup_id="USA-TX42500-X", start_date_time="2020-10-23T21:00Z")
    ```

* To fetch the top 5 genres with the highest movie count along with the movie details

    ```bash
    (venv) --- Personal/tmsapi ‹master* ?› » ipython
    Python 3.8.1 (v3.8.1:1b293b6006, Dec 18 2019, 14:08:53)
    Type 'copyright', 'credits' or 'license' for more information
    IPython 7.18.1 -- An enhanced Interactive Python. Type '?' for help.
    
    In [1]: import tmsapi
    2020-10-24 19:47:57,291 INFO sqlalchemy.engine.base.Engine SHOW VARIABLES LIKE 'sql_mode'
    ...
    2020-10-24 19:47:57,299 INFO sqlalchemy.engine.base.Engine {}
    
    In [2]: tmsapi.group_and_rank_movies_by_genre()
    2020-10-24 19:48:02,594 INFO sqlalchemy.engine.base.OptionEngine SELECT theatre_movies.id, theatre_movies.title, theatre_movies.release_year, theatre_movies.genres, theatre_movies.description, theatre_movies.theatre
    FROM theatre_movies
    ...
    2020-10-24 19:48:02,599 INFO sqlalchemy.engine.base.OptionEngine {}
    Out[2]:
         index   id                title  ...  theatre num_movies channel
    285    183  184      Rock the Kasbah  ...      NaN         70     531
    495    393  394          Bring It On  ...      NaN         70     602
    120     18   19  The Nutty Professor  ...      NaN         70     582
    338    236  237           Wanderlust  ...      NaN         70     542
    515    413  414            Good Boys  ...      NaN         70     523
    
    [5 rows x 9 columns
    ```
