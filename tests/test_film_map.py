from web_map.main import (
    create_layer,
    create_html_popup,
    get_films_info,
    get_films_info_from_csv,
    find_location,
    find_distance,
    find_closest_locations,
    find_films_in_location,
)
import pandas as pd
import folium


def test_create_layer():
    assert isinstance(
        create_layer(
            pd.DataFrame(
                [["Name", "Year", "Location", (10, 10)]],
                columns=["Name", "Year", "Location", "Coordinates"],
            ),
            "layer",
        ),
        folium.FeatureGroup,
    )
    assert isinstance(
        create_layer(
            pd.DataFrame(columns=["Name", "Year", "Location", "Coordinates"]),
            "layer",
        ),
        folium.FeatureGroup,
    )


def test_create_html_popup():
    assert isinstance(create_html_popup(["First", "Second"]), str)
    assert isinstance(create_html_popup([]), str)
    assert isinstance(create_html_popup(["First", "Second"]), str)


def test_get_films_info():
    assert isinstance(get_films_info("locations.list"), pd.DataFrame)
    assert isinstance(get_films_info(""), pd.DataFrame)


def test_get_films_info_from_csv():
    assert isinstance(get_films_info_from_csv("locations_250000.csv"), pd.DataFrame)
    assert isinstance(get_films_info_from_csv(""), pd.DataFrame)


def test_find_location():
    assert find_location("Ukraine") == (49.4871968, 31.2718321)
    assert find_location("") == (-69, -179)


def test_find_distance():
    assert round(find_distance((60, 150), (30, 15)), 5) == 9217.59933
    assert find_distance((0, 0), (0, 0)) == 0.0


def test_find_closest_locations():
    assert isinstance(
        find_closest_locations(
            pd.DataFrame(
                [["Name", 1960, "location", (10, 10)]],
                columns=["Name", "Year", "Location", "Coordinates"],
                index=[0],
            ),
            (15, 15),
            1960,
        ),
        pd.DataFrame,
    )


def test_find_films_in_location():
    assert isinstance(
        find_films_in_location(
            pd.DataFrame(
                [["Name", 1960, "Ukraine", (10, 10)]],
                columns=["Name", "Year", "Location", "Coordinates"],
                index=[0],
            )
        ),
        pd.DataFrame,
    )
