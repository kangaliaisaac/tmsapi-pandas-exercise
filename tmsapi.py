#!/usr/bin/python3

import os
import pandas as pd
import requests
import sqlalchemy

from sqlalchemy.ext.declarative import declarative_base


API_SECRET = os.getenv("API_SECRET")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

BASE_URL = "http://data.tmsapi.com/v1.1/movies/"
MOVIE_TYPES = ["SHOWINGS", "AIRINGS"]

engine = sqlalchemy.create_engine(
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@localhost:3306/{DB_NAME}",
    echo=True
)
Base = declarative_base()


class TheatreMovie(Base):
    __tablename__ = "theatre_movies"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    title = sqlalchemy.Column(sqlalchemy.String(length=255))
    release_year = sqlalchemy.Column(sqlalchemy.Integer)
    genres = sqlalchemy.Column(sqlalchemy.Text)
    description = sqlalchemy.Column(sqlalchemy.Text)
    theatre = sqlalchemy.Column(sqlalchemy.String(length=50))

    def __repr__(self):
        return (f"<TheatreMovie(title='{self.title}', "
                f"releaseYear='{self.release_year}', "
                f"genres='{self.genres}', "
                f"theatre='{self.theatre}')>")


class TVMovie(Base):
    __tablename__ = "tv_movies"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    title = sqlalchemy.Column(sqlalchemy.String(length=255))
    release_year = sqlalchemy.Column(sqlalchemy.Integer)
    genres = sqlalchemy.Column(sqlalchemy.Text)
    description = sqlalchemy.Column(sqlalchemy.Text)
    channel = sqlalchemy.Column(sqlalchemy.String(length=50))

    def __repr__(self):
        return (f"<TVMovie(title='{self.title}', "
                f"releaseYear='{self.release_year}', "
                f"genres='{self.genres}', "
                f"channel='{self.channel}')>")


Base.metadata.create_all(engine)

Session = sqlalchemy.orm.session.sessionmaker()
Session.configure(bind=engine)
session = Session()


class BadRequest(Exception):
    pass


def unique(list_obj):
    seen = set()
    new_list = []
    for each in list_obj:
        if each in seen:
            continue
        new_list.append(each)
        seen.add(each)
    return new_list


def fetch_data_from_api(
        data_for,
        zip_code=None,
        start_date=None,
        lineup_id=None,
        start_date_time=None):
    """
    Parameters required to get movies playing in local theatres in US for
    a particular zip code and start date (SHOWINGS):
    - api_secret
    - zip_code
    - start_date

    Parameters required to get movies airing on TV for a particular line up
    and date and time (AIRINGS):
    - api_secret
    - lineup_id
    - start_date_time
    """
    # Perform preliminary checks on the inputs to make sure the required
    # parameters for showings or airings have been passed in
    if data_for not in MOVIE_TYPES:
        raise ValueError(
            f"{data_for} should either be 'SHOWINGS' or 'AIRINGS'.")
    if data_for == "SHOWINGS" and (zip_code and start_date) is None:
        raise ValueError(
            "For showings, both the zip_code and the start_date are required.")
    if data_for == "AIRINGS" and (lineup_id and start_date_time) is None:
        raise ValueError(
            "For airings, both the line_up_id and the start_date_time "
            "are required.")

    # Once we are confident the required parameters have been passed in, we
    # compose the API_URL and make the request
    if data_for == "AIRINGS":
        query_params = {
            "lineupId": lineup_id,
            "startDateTime": start_date_time,
            "api_key": API_SECRET
        }
        response = requests.get(f"{BASE_URL}airings?", params=query_params)
        # We are guaranteed to get a response object, whether an empty array
        # or one with objects in it
        if response.status_code == 200:
            for payload in response.json():
                airing = TVMovie(
                    title=payload["program"]["title"],
                    release_year=payload["program"]["releaseYear"],
                    genres=", ".join(payload["program"]["genres"]),
                    description=payload["program"].get(
                        "longDescription", payload["program"].get(
                            "shortDescription", "")),
                    channel=payload["station"]["channel"]
                )
                session.add(airing)
                session.commit()
        else:
            raise BadRequest(response.json(), response.status_code)
    else:
        query_params = {
            "zip": zip_code,
            "startDate": start_date,
            "api_key": API_SECRET
        }
        response = requests.get(f"{BASE_URL}showings?", params=query_params)
        # We are guaranteed to get a response object, whether an empty array
        # or one with objects in it
        if response.status_code == 200:
            for payload in response.json():
                showing = TheatreMovie(
                    title=payload["title"],
                    release_year=payload.get("releaseYear"),
                    genres=", ".join(payload.get("genres", [])),
                    description=payload.get(
                        "longDescription", payload.get("shortDescription", "")),
                    theatre=", ".join(unique([
                        theatre["theatre"]["id"]
                        for theatre in payload["showtimes"]
                    ]))
                )
                session.add(showing)
                session.commit()
        else:
            raise BadRequest(response.json(), response.status_code)


def group_and_rank_movies_by_genre():
    # Group both the Movie lists based on ‘Genre’
    theatre_movies_df = pd.read_sql(
        session.query(TheatreMovie).statement, session.bind)
    channel_movies_df = pd.read_sql(
        session.query(TVMovie).statement, session.bind)

    def _count(group):
        c = group["genres"].count()
        group["num_movies"] = c

        return group

    tf = theatre_movies_df.groupby("genres").apply(_count).reset_index()
    cf = channel_movies_df.groupby("genres").apply(_count).reset_index()

    # Combine the movie lists (Theatre and Channel movies) based on the Genres
    merged = pd.concat(
        [tf, cf], ignore_index=True, axis=0).sort_values(
        "num_movies", ascending=False)

    # Return the Top 5 Genres with the highest movie count along with
    # the movie details
    return merged.drop_duplicates(subset=["title"]).head()
