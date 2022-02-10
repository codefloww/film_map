"""module for web map with films locations in certain years"""
import argparse
import functools
from typing import Dict, List, Tuple, Union
import folium
import pandas as pd


def create_map(
    path: str,
    location: Tuple[float, float],
    year: int,
    fast_procesing: bool,
    opened: bool,
) -> None:
    """creates web map of films from database

    Args:
        path (str): path to file with films
        location (Tuple[float, float]): latitude and longtitude of current location
        year (int): year of films to search for in closest layer
        fast_procesing (bool): using preprocesed dataset
        opened (bool): open web map after generating it
    """
    # create map/html
    map = folium.Map(location=location, zoom_start=5, control_scale=True)
    if fast_procesing:
        films = get_films_info_from_csv(path)
    else:
        films = get_films_info(path)
    local_films = find_films_in_location(films)
    closest_films = find_closest_locations(films, location, str(year))
    local_films_layer = create_layer(local_films, "Films in location")
    closest_films_in_year_layer = create_layer(
        closest_films, f"Closest films in {year}"
    )
    # create marker for user location
    current_location = folium.CircleMarker(
        location=location,
        radius=15,
        popup="Я тут)",
        fill_color="green",
        color="green",
        fill_opacity=0.5,
    )
    map.add_child(current_location)
    map.add_child(local_films_layer)
    map.add_child(closest_films_in_year_layer)
    map.add_child(folium.LayerControl())
    map.save("Film_map.html")
    if opened:
        open_web_map("Film_map.html")


def create_layer(films: pd.DataFrame, name: str) -> folium.FeatureGroup:
    """creates layer for web map

    Args:
        films (pd.DataFrame): films for layer
        name (str): name of the layer in the web map

    Returns:
        folium.FeatureGroup: web map layer with films
    """
    # dictionary for assigning to marker popup multiple films
    films_locations: Dict[str, List[Tuple[str, str]]] = dict()
    for i in range(len(films)):
        if str(films.iloc[i]["Coordinates"]) in films_locations.keys():
            films_locations[str(films.iloc[i]["Coordinates"])].append(
                (films.iloc[i]["Name"], films.iloc[i]["Year"])
            )
        else:
            films_locations[str(films.iloc[i]["Coordinates"])] = [
                (films.iloc[i]["Name"], films.iloc[i]["Year"])
            ]
    # create layer for map
    films_layer = folium.FeatureGroup(name=name)
    for i in range(len(films)):
        film_coordinates = films.iloc[i]["Coordinates"]
        iframe = folium.IFrame(
            html=create_html_popup(films_locations[str(films.iloc[i]["Coordinates"])]),
            width=250,
            height=100,
        )
        films_layer.add_child(
            folium.Marker(
                location=film_coordinates,
                popup=folium.Popup(iframe),
                icon=folium.Icon(),
            )
        )
    return films_layer


def create_html_popup(films: List[Tuple[str, str]]) -> str:
    """creates html_template for popup window

    Args:
        films (List[Tuple[str, str]]): films for this popup

    Returns:
        str: html string to be showed in popup
    """
    html_template = "Films:"
    for film in films:
        html_template += f"""<br>
        <a href="https://www.google.com/search?q=%22{film[0].strip('"')}%22"
        target="_blank">{film[0], film[1]}</a><br>
        """
    return html_template


def get_films_info(path: str) -> pd.DataFrame:
    """reads file, converts it by lines in dataframe

    Args:
        path (str): path to file with films

    Returns:
        pd.DataFrame: dataframe consisting of films' names,\
        years and locations
    """
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as data:
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
        films_df = pd.DataFrame(films[:-1], columns=["Name", "Year", "Location"])

    except FileNotFoundError:
        print("There is no such file")
        films_df = pd.DataFrame(columns=["Name", "Year", "Location"])

    return films_df


def get_films_info_from_csv(path: str) -> pd.DataFrame:
    """gets films' name,year,location,coordinates from csv file into dataframe

    Args:
        path (str): path to csv file

    Returns:
        pd.DataFrame: films with names, year, locations and coords
    """
    import ast

    try:
        films = pd.read_csv(path, converters={"Coordinates": ast.literal_eval})

    except FileNotFoundError:
        print("There is no such file with this path")
        films = pd.DataFrame(columns=["Name", "Year", "Location", "Coordinates"])

    return films


@functools.lru_cache(maxsize=512000)
def find_location(place: str) -> Tuple[float, float]:
    """finds coords of address

    Args:
        place (str): address in format of buildinge,\
            street,town,country

    Raises:
        GeocoderUnavailable: invalid address or address which is not in database

    Returns:
        Tuple[float, float]: latitude and longtitude coords of location
    """
    from geopy.exc import GeocoderUnavailable
    from geopy.geocoders import Nominatim
    # utility for finding location
    geolocator = Nominatim(user_agent="my-request")
    if place in ["", " ", ",", ", "]:
        return -69.0, -179.0
    try:
        location = geolocator.geocode(place)
        if location is None:
            raise GeocoderUnavailable
    except GeocoderUnavailable:
        return find_location(", ".join(place.split(", ")[1:]))
    return location.latitude, location.longitude


def find_distance(
    coords_1: Tuple[float, float], coords_2: Tuple[float, float]
) -> Union[float, None]:
    """finds distance between two points on Earth using haversin

    Args:
        coords_1 (Tuple[float, float]): coordinates of first point
        coords_2 (Tuple[float, float]): coordinates of second point

    Returns:
        Union[float, None]: distance between two points
    """
    import geopy.distance

    return float(geopy.distance.distance(coords_1, coords_2).km)


def find_closest_locations(
    films: pd.DataFrame, location: Tuple[float, float], year: str
) -> pd.DataFrame:
    """finds closest films' locations to given location in certain year

    Args:
        films (pd.DataFrame): films with year and locations
        location (Tuple[float, float]): your given locatoins closest to which you search
        year (str): year of films to search for

    Returns:
        pd.DataFrame: closest films of that year to location
    """
    # filter df and add coords to df if needed
    year_films = films.loc[films["Year"] == year]
    if "Coordinates" not in year_films.columns:
        year_films["Coordinates"] = year_films["Location"].apply(find_location)
    closest_films = pd.DataFrame(
        columns=["Name", "Year", "Location", "Coordinates", "Distance"]
    )
    year_films["Distance"] = year_films["Coordinates"].apply(
        lambda x: find_distance(location, x)
    )
    # find and create df with closest films
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
    return closest_films


def find_films_in_location(films: pd.DataFrame) -> pd.DataFrame:
    """finds films filmed in certain location

    Args:
        films (pd.DataFrame): films with their locations

    Returns:
        pd.DataFrame: films which were filmed in certain location
    """
    films.dropna(inplace=True)
    # change for more precise address for better performance
    local_films = films.loc[films["Location"].str.contains("Ukraine")]
    if "Cooridinates" not in local_films.columns:
        local_films["Coordinates"] = local_films["Location"].apply(find_location)
    return local_films


def open_web_map(name: str) -> None:
    """open web map(html file) in browser

    Args:
        name (str): name of the web map(html file)
    """
    import os
    import webbrowser
    # open in new tab with url
    new = 2
    url = "file://" + os.path.realpath(name)
    webbrowser.open(url, new=new)


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
        "--lat",
        type=float,
        default=49.817545,
        help="Latitude for your location (default:49.817545)",
    )
    parser.add_argument(
        "--lng",
        type=float,
        default=24.023932,
        help="Longtitude for your location (default:24.023932)",
    )
    parser.add_argument("--opened", action="store_true", help="Instantly opens web map")
    args = parser.parse_args()
    print("Start generating web map")
    if args.fast:
        create_map(
            "locations_250000.csv",
            (args.lat, args.lng),
            args.year,
            args.fast,
            args.opened,
        )
    else:
        create_map(
            args.path,
            (args.lat, args.lng),
            args.year,
            args.fast,
            args.opened,
        )
    print("Completed")
