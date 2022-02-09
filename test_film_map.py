import unittest
import main
import pandas as pd
import folium


class TestFimlsMap(unittest.TestCase):
    def test_create_layer(self):
        self.assertIsInstance(
            main.create_layer(
                pd.DataFrame(
                    [["Name", "Year", "Location", (10, 10)]],
                    columns=["Name", "Year", "Location", "Coordinates"],
                ),
                "layer",
            ),
            folium.FeatureGroup,
        )
        self.assertIsInstance(
            main.create_layer(
                pd.DataFrame(columns=["Name", "Year", "Location", "Coordinates"]),
                "layer",
            ),
            folium.FeatureGroup,
        )

    def test_create_html_template(self):
        self.assertIsInstance(main.create_html_popup(["First", "Second"]), str)
        self.assertIsInstance(main.create_html_popup([]), str)
        self.assertIsInstance(main.create_html_popup(["First", "Second"]), str)
        self.assertRaises(IndexError, main.create_html_popup, [""])

    def test_get_films_info(self):
        self.assertIsInstance(main.get_films_info("locations.list"), pd.DataFrame)
        self.assertIsInstance(main.get_films_info(""), pd.DataFrame)

    def test_get_films_info_from_csv(self):
        self.assertIsInstance(
            main.get_films_info_from_csv("locations_250000.csv"), pd.DataFrame
        )
        self.assertIsInstance(main.get_films_info_from_csv(""), pd.DataFrame)

    def test_find_location(self):
        self.assertEqual(main.find_location("Ukraine"), (49.4871968, 31.2718321))
        self.assertEqual(main.find_location(""), (-69, -179))

    def test_find_distance(self):
        self.assertEqual(main.find_distance((60, 150), (30, 15)), 9217.599329357261)
        self.assertEqual(main.find_distance((0, 0), (0, 0)), 0.0)

    def test_find_closest_locations(self):
        self.assertIsInstance(
            main.find_closest_locations(
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

    def test_find_films_in_location(self):
        self.assertIsInstance(
            main.find_films_in_location(
                pd.DataFrame(
                    [["Name", 1960, "Ukraine", (10, 10)]],
                    columns=["Name", "Year", "Location", "Coordinates"],
                    index=[0],
                )
            ),
            pd.DataFrame,
        )


if __name__ == "__main__":
    unittest.main()
