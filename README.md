# film_map
Film_map is a project that creates web map of films based on names, locations and year of film producing.

## Desription
It utilizes python with a few module such as folium, geopy, pandas and few other, as well as some html knowledge. Main functionality is based on getting films info from files and finding their coordinates. This option can take quite a lot time so I recommend using already preprocessed file from project.

## Installation
You can use simple git clone command in your directory to download project.
```bash
git clone git@github.com:codefloww/film_map.git
```
There is possible need in ssh token in case of problems with downloading
 Also you can install this project using pip install
```bash
pip install -e git+https://github.com/codefloww/film_map#egg=film_map
```
You also need to install dependencies for module after entering in project directory
```bash
pip install -r requirements.txt
```

## Usage
Use the project via terminal
If you're in project directory:
```bash
python src/web_map/main.py -h
```
There are a few options which you can use(info by -h or --help)
More of the functions also in Example(Example.md)
Also you can use the package manager pip to use functions for project module
```bash
pip install web-map
```
```python
import web_map
web_map.<main or create_file>.<functionname>(*args, **kwargs)
```
## Example
You can use this module with your own dataset file(in this case it need to be in same format as those in project) 
or with given in project. The result will have similar look as [*Film_map.html*](Film_map.html). 
To run module you need to run in terminal with some arguments
```bash
python src/web_map/main.py --fast --year 2004 --opened
```
![Example of generated web map](/assets/images/Web_map_example.jpg)
The result of such command will be web map(generated from [*locations_250000.csv*](locations_250000.csv) and closest films in 2004) and opened in web browser. You can also pass your coordinates and your own file instead of given.
**Warning!**
If you are going to use your own file with no coordinates you should choose one of further years and change location for search in [*main.py*](src/web_map/main.py) in find_films_in_location to more precise one.

## Contributing
I'll be very happy to have any feedback. Pull requests are welcome. There is a lot of possible
improvment to this project. For more comfortable contribution there are provided some tests tools.

## Tests
![Tests](https://github.com/codefloww/film_map/actions/workflows/tests.yml/badge.svg)
In case you want to use tests for this project, you need to install some packages additionaly to installing process.
```bash
pip install -r requirements_dev.txt
```
You can use pytest, mypy, flake8 or tox for testing this project. 
```bash
mypy src
pytest
flake8 src
tox
```
As far as I know, this project should correctly work with python3.8 and newer. I'll be greatful for further testing.

## License
[MIT]
(https://choosealicense.com/licenses/mit/)
