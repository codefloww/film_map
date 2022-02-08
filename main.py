"""module for web map with films locations in certain years"""
from cgitb import html
import pandas
import folium
from functools import cache
import argparse


def create_map(path: str, location: tuple, year: int, fast_procesing: bool) -> object:

    map = folium.Map(location=location, zoom_start=5, control_scale=True)
    if fast_procesing:
        films = get_films_info_from_csv(path)  # getting films from csv with coordinates
    else:
        films = get_films_info(path)  # getting films from list
    local_films = find_films_in_Lviv(films)
    closest_films = find_closest_locations(films, location, str(year))
    local_films_layer = create_layer(local_films, "local films")
    closest_films_in_year_layer = create_layer(closest_films, "closest films")

    map.add_child(local_films_layer)
    map.add_child(closest_films_in_year_layer)
    map.add_child(folium.LayerControl())
    map.save("Film_map.html")


def create_layer(films, name):
    films_locations = dict()
    for i in range(len(films)):
        if str(films.iloc[i]["Coordinates"]) in films_locations.keys():
            films_locations[str(films.iloc[i]["Coordinates"])].append(
                (films.iloc[i]["Name"], films.iloc[i]["Year"])
            )
        else:
            films_locations[str(films.iloc[i]["Coordinates"])] = [
                (films.iloc[i]["Name"], films.iloc[i]["Year"])
            ]
    films_layer = folium.FeatureGroup(name=name)
    for i in range(len(films)):
        # film_name = films.iloc[i]["Name"]
        # film_year = films.iloc[i]["Year"]
        # film_location = films.iloc[i]["Location"]
        film_coordinates = films.iloc[i]["Coordinates"]
        films_layer.add_child(
            folium.Marker(
                location=film_coordinates,
                # popup=f"{film_name}\n{film_year}\n{film_location}",
                popup=create_html_popup(
                    films_locations[str(films.iloc[i]["Coordinates"])]
                ),
                icon=folium.Icon(),
            )
        )
    return films_layer


def create_html_popup(films):
    html_template = """Films:"""
    for film in films:
        html_template += f"""<br>
        <a href="https://www.google.com/search?q=%22{film[0]}%22"
        target="_blank">{film[0], film[1]}</a><br>
        """
    return html_template


def get_films_info(path: str) -> object:
    with open(path, "r", encoding="utf-8", errors="ignore") as data:
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
    films = pandas.DataFrame(films[:-1], columns=["Name", "Year", "Location"])
    return films


def get_films_info_from_csv(path):
    import ast

    films = pandas.read_csv(path, converters={"Coordinates": ast.literal_eval})
    return films


@cache
def find_location(place: str):
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderUnavailable

    geolocator = Nominatim(user_agent="my-request")
    try:
        location = geolocator.geocode(place)
        if location == None:
            raise GeocoderUnavailable
    except GeocoderUnavailable:
        return find_location(", ".join(place.split(", ")[1:]))
    return location.latitude, location.longitude


def find_distance(coords_1, coords_2):
    import geopy.distance

    return geopy.distance.distance(coords_1, coords_2).km


def find_closest_locations(films, location, year):
    year_films = films.loc[films["Year"] == year]
    if "Coordinates" not in year_films.columns:
        year_films["Coordinates"] = year_films["Location"].apply(find_location)
    closest_films = pandas.DataFrame(
        columns=["Name", "Year", "Location", "Coordinates", "Distance"]
    )
    year_films["Distance"] = year_films["Coordinates"].apply(
        lambda x: find_distance(location, x)
    )
    for i in range(len(year_films)):
        film_location = year_films.iloc[i]["Coordinates"]
        geo_distance = find_distance(location, film_location)
        if len(closest_films) < 5:
            closest_films = closest_films.append(year_films.iloc[i], ignore_index=True)
            closest_films.sort_values(by="Distance", ascending=False)
        elif (
            len(closest_films) == 5
            and geo_distance < closest_films["Distance"].values[-1]
        ):
            closest_films.drop(closest_films.tail().index, inplace=True)
            closest_films = closest_films.append(year_films.iloc[i], ignore_index=True)
            closest_films.sort_values(by="Distance", ascending=False, inplace=True)
    print(closest_films)
    return closest_films


def find_films_in_Lviv(films):
    films.dropna(inplace=True)
    local_films = films.loc[films["Location"].str.contains("Lviv")]
    # local_films.info()
    if "Cooridinates" not in local_films.columns:
        local_films["Coordinates"] = local_films["Location"].apply(find_location)
    # print(local_films)
    return local_films


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""Film map. \n
This program creates web map with films which are 5 closest to given location in certain year and
films which were filmed in Lviv""",
        usage="You type required arguments and it run program which creates html file with map",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--path",
        type=str,
        help="Path to list with information about films",
    )
    group.add_argument(
        "--fast",
        action="store_true",
        help="This is the argument for smaller database and faster work of program",
    )
    parser.add_argument(
        "--year",
        type=int,
        default=1900,
        help="Year of films for closest (default: 1900)",
    )
    parser.add_argument(
        "--lat", type=float, default=49.817545, help="Latitude for your location"
    )
    parser.add_argument(
        "--lng", type=float, default=24.023932, help="Longtitude for your location"
    )
    args = parser.parse_args()
    if args.fast:
        create_map("locations_250000.csv", (args.lat, args.lng), args.year, args.fast)
    else:
        create_map(args.path, (args.lat, args.lng), args.year, args.fast)
