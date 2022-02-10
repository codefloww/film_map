"""Allows to create csv file with coordinates for locations from list"""
import functools
import pandas as pd
from typing import Tuple


def get_films_info(path: str) -> pd.DataFrame:
    """reads file, converts it by lines in dataframe

    Args:
        path (str): path to file with films

    Returns:
        pd.DataFrame: dataframe consisting of films' names,\
        years and locations
    """
    try:
        with open(path, "r", errors="ignore") as data:
            for _ in range(14):
                data.readline()
            films_data = data.readlines()
            films = []
        for film in films_data:
            if film[-2] == ")":
                name_and_year, place = film.split("\t")[0], film.split("\t")[-2]
            else:
                name_and_year, place = film.split("\t")[0], film.split("\t")[-1][:-1]
            year_start = name_and_year.find("(")
            films.append([
                name_and_year[: year_start - 1],
                name_and_year[year_start + 1: year_start + 5],
                place,
            ])
        films = pd.DataFrame(films[:-1], columns=["Name", "Year", "Location"])
        return films[:10:2]  # which size of original file you need
    except FileNotFoundError:
        print("There is no such file")
        films = pd.DataFrame(columns=["Name", "Year", "Location"])
        return films


@functools.lru_cache(maxsize=500000)
def find_location(place: str) -> Tuple[float, float]:
    """finds coordinates of address

    Args:
        place (str): address in format of buildinge,\
            street,town,country

    Raises:
        GeocoderUnavailable: invalid address or address which is not in database

    Returns:
        Tuple[float, float]: latitude and longtitude coords of location
    """
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderUnavailable

    geolocator = Nominatim(user_agent="my-request", timeout=3)
    try:
        location = geolocator.geocode(place)
        print(location)
        if location is None:
            raise GeocoderUnavailable
    except GeocoderUnavailable:
        if "," not in place:
            return -69, -179
        else:
            return find_location(", ".join(place.split(", ")[1:]))
    return location.latitude, location.longitude


if __name__ == "__main__":
    films = get_films_info("locations.list")
    films["Coordinates"] = films["Location"].apply(find_location)
    films.to_csv("s_locations.csv", index=False)
