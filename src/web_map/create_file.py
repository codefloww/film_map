"""Allows to create csv file with coordinates for locations from list"""
from functools import cache
import pandas as pd


def get_films_info(path: str) -> pd.DataFrame:
    with open(path, "r", errors="ignore") as data:
        for _ in range(14):
            data.readline()
        films = data.readlines()

    for i, film in enumerate(films):
        if film[-2] == ")":
            name_and_year, place = film.split("\t")[0], film.split("\t")[-2]
        else:
            name_and_year, place = film.split("\t")[0], film.split("\t")[-1][:-1]
        year_start = name_and_year.find("(")
        films[i] = [
            name_and_year[: year_start - 1],
            name_and_year[year_start + 1 : year_start + 5],
            place,
        ]
    films = pd.DataFrame(films[:-1], columns=["Name", "Year", "Location"])
    return films[:10:2]  # which size of original file you need


@cache
def find_location(place: str) -> tuple[float, float]:
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
            return -179, -179
        else:
            return find_location(", ".join(place.split(", ")[1:]))
    return location.latitude, location.longitude


if __name__ == "__main__":
    films = get_films_info("locations.list")
    films["Coordinates"] = films["Location"].apply(find_location)
    films.to_csv("s_locations.csv", index=False)
