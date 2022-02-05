"""module for web map with films locations in certain years"""
import pandas
import folium
from functools import cache


def create_map(location: tuple) -> object:

    films = get_films_info("locations.list")
    map = folium.Map(location=location, zoom_start=5, control_scale=True)
    local_films_layer = folium.FeatureGroup(name=" local films")
    closest_films_in_year_layer = folium.FeatureGroup(name="closest films")
    local_films = find_films_in_Lviv(films)
    # films_layer.add_child(folium.Marker(location=films["Location"],popup=films['Name'],icon = folium.Icon()))
    # closest_films_in_year_layer.add_child(folium.Marker(location=film_location,popup = film_name+'\n'+str(film_year), icon = folium.Icon()))

    for i in range(len(local_films)):
        film_name = local_films.iloc[i]["Name"]
        film_year = local_films.iloc[i]["Year"]
        film_location = local_films.ilco[i]["Location"]
        film_coordinates = local_films.iloc[i]["Coordinates"]
        local_films_layer.add_child(
            folium.Marker(location=film_coordinates, popup=f'{film_name}\n{film_year}\n{film_location}', icon=folium.Icon())
        )

    closest_films = find_closest_locations(films, location, "1906")
    for i in range(len(closest_films)):
        film_name = closest_films.iloc[i]["Name"]
        film_year = closest_films.iloc[i]["Year"]
        film_location = closest_films.iloc[i]["Location"]
        film_coordinates = closest_films.iloc[i]["Coordinates"]
        closest_films_in_year_layer.add_child(
            folium.Marker(location=film_coordinates, popup=f'{film_name}\n{film_year}\n{film_location}', icon=folium.Icon())
        )
    map.add_child(local_films_layer)
    map.add_child(closest_films_in_year_layer)
    map.add_child(folium.LayerControl())
    map.save("Map_1.html")


def get_films_info(path: str) -> object:
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
    films = pandas.DataFrame(films[:-1], columns=["Name", "Year", "Location"])
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
    local_films = films.loc[films["Location"].str.contains("Lviv")]
    print(local_films)
    local_films["Coordinates"] = local_films["Location"].apply(find_location)
    return local_films


if __name__ == "__main__":
    location = [49.817545, 24.023932]
    create_map(location)
