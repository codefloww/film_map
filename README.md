# film_map
Film_map is a project that creates web map of films based on names, locations and year of film producing.

## Description
It utilizes python with a few module such as folium, geopy, pandas and few other, as well as some html knowledge. Main functionality is based on getting films info from files and finding their coordinates. This option can take quite a lot of time so I recommend using already preprocessed file from project.

## Installation
I recommend you to set up virtual environment before installing(for unix systems). Follow pretty similar way for Windows except path.
```bash
python3 -m venv venv
python3 -m pip install --upgrade pip setuptools wheel
source venv/bin/activate
```
You can use simple git clone command in your directory to download project.
```bash
git clone git@github.com:codefloww/film_map.git
```
There is possible need in ssh token in case of problems with downloading.

Also, you can install this project using pip install.(recommended)
```bash
pip3 install -e git+https://github.com/codefloww/film_map#egg=web-map
```
You also need to install dependencies for module. To do this, make the project folder 'web-map' your working directory.
```bash
pip install -r requirements.txt
```


## Usage
Use the project via terminal if you're in project directory:
```bash
python3 src/web_map/main.py -h
```
There are a few options which you can use(info by -h or --help).
More of the functions also in [Example](#example).

Also, you can use the package manager pip to use functions from project module.
```bash
pip3 install web-map
```
```python
import web_map
web_map.<main or create_file>.<functionname>(*args, **kwargs)
```
## Example
You can use this module with your own dataset file(in this case it needs to be in the same format as those in project) 
or with given in project. The result will have similar look as [*Film_map.html*](Film_map.html). 
To run module you need to run in terminal with some arguments.
```bash
python3 src/web_map/main.py --fast --year 2004 --opened
```
![Example of generated web map](/assets/images/Web_map_example.jpg)
The result of such command will be web map(generated from [*locations_250000.csv*](locations_250000.csv) and closest films in 2004) and opened in web browser. You can also pass your coordinates and your own file instead of given.

**Warning!**
If you are going to use your own file with no coordinates you should choose one of the further years and change location for search in [*main.py*](src/web_map/main.py) in find_films_in_location to more precise one. In general with --fast option map will generate about 1 minute for default configuration. With no preprocessed list map can generate for as long as you can imagine.

## Contributing
I'll be very happy to have any feedback. Pull requests are welcome. There is a lot of possible
improvement to this project. For more comfortable contribution there are provided some tests tools.

## Tests
![Tests](https://github.com/codefloww/film_map/actions/workflows/tests.yml/badge.svg)

In case you want to use tests for this project, you need to install some packages additionally to installing process.
```bash
pip3 install -r requirements_dev.txt
```
You can use pytest, mypy, flake8 or tox for testing this project. 
```bash
mypy src
pytest
flake8 src
tox
```
You can find and add new tests in [*test_film_map.py*](/tests/test_film_map.py)
As far as I know, this project should correctly work with python3.8 and newer. I'll be keen on further testing.

## License
[MIT](https://choosealicense.com/licenses/mit/)
