from functools import cache, lru_cache
import pandas

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
    return films[:1000]
@cache
def find_location(place:str):
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderUnavailable
    geolocator = Nominatim(user_agent='my-request',timeout=1)
    # if place in ['',' ']:
    #     return -179,-179
    try:
        location = geolocator.geocode(place)
        if location == None:
            raise GeocoderUnavailable
    except GeocoderUnavailable:
        # return find_location(', '.join(place.split(', ')[1:]))
        return -179, -179
    return location.latitude, location.longitude

    

if __name__ == "__main__":
    films = get_films_info('locations.list')
    films['Coordinates'] = films['Location'].apply(find_location)
    films.to_csv('locations.csv')