"""module for web map with films locations in certain years"""
import pandas
import folium

def create_map(location: tuple) -> object:

    films = get_films_info('locations.list')
    films['Coordinates'] = films['Location'].apply(find_location)
    map = folium.Map(location=location, zoom_start=5,control_scale=True)
    films_layer = folium.FeatureGroup(name = 'films')
    closest_films_in_year_layer = folium.FeatureGroup(name = 'closest films')

    # films_layer.add_child(folium.Marker(location=films["Location"],popup=films['Name'],icon = folium.Icon()))
    # closest_films_in_year_layer.add_child(folium.Marker(location=film_location,popup = film_name+'\n'+str(film_year), icon = folium.Icon()))

    for i in range(len(films)):
        film_name = films.iloc[i]["Name"]
        film_year = films.iloc[i]["Year"]
        film_location = films.iloc[i]["Coordinates"]
        films_layer.add_child(folium.Marker(location=film_location,popup = film_name, icon = folium.Icon()))
    
    closest_films = find_closest_locations(films,location,'2006')
    for i in range(len(closest_films)):
        film_name = closest_films.iloc[i]["Name"]
        film_year = closest_films.iloc[i]["Year"]
        film_location = closest_films.iloc[i]["Coordinates"]
        closest_films_in_year_layer.add_child(folium.Marker(location=film_location,popup = film_name, icon = folium.Icon()))
    map.add_child(films_layer)
    map.add_child(closest_films_in_year_layer)
    map.add_child(folium.LayerControl())
    map.save("Map_1.html")


def get_films_info(path:str) -> object:
    with open(path, "r", errors="ignore") as data:
        for _ in range(14):
            data.readline()
        films = data.readlines()

    for i, film in enumerate(films):
        if film[-2] == ')':
            name_and_year, place = film.split("\t")[0], film.split("\t")[-2]
        else:
            name_and_year, place = film.split("\t")[0], film.split("\t")[-1][:-1]
        year_start = name_and_year.find("(")
        films[i] = [
            name_and_year[: year_start - 1],
            name_and_year[year_start + 1 : year_start + 5],
            place,
        ]
    films = pandas.DataFrame(films[:-1],columns=['Name','Year','Location'])
    return films[:10]


def find_location(place:str):
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderUnavailable
    geolocator = Nominatim(user_agent='my-request')
    try:
        location = geolocator.geocode(place)
        if location == None:
            return -179,-179
            raise GeocoderUnavailable
    except GeocoderUnavailable:
        return find_location(', '.join(place.split(', ')[1:]))
    return location.latitude, location.longitude


def find_distance(coords_1,coords_2):
    import geopy.distance

    return geopy.distance.distance(coords_1,coords_2).km


def find_closest_locations(films, location, year):
    year_films = films.loc[films["Year"] == year]
    closest_films = pandas.DataFrame(columns=['Name','Year','Location','Coordinates','Distance'])
    for i in range(len(year_films)):
        film_location = year_films.iloc[i]["Coordinates"]
        geo_distance = find_distance(location, film_location)
        if len(closest_films)<5:
            year_films.iloc[i]['Distance'] = geo_distance
            closest_films = closest_films.append(year_films.iloc[i],ignore_index=True)
            print(closest_films)
            closest_films.sort_values(by = 'Distance',ascending=False)
        elif len(closest_films) == 5 and geo_distance<closest_films.last()["Distance"]:
            closest_films.drop(closest_films.tail().index,inplace=True)
            closest_films = closest_films.append(year_films.iloc[i],ignore_index=True)
            closest_films.sort_values(by = 'Distance',ascending=False,inplace=True)
    return closest_films  

if __name__ == "__main__":
    location = [49.817545, 24.023932]
    create_map(location)