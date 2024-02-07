# Routing module
## Description
This module is used to display the routing page of the website.

The package was mainly inspired by the following tutorials :
- [Route optimization with python](https://towardsdatascience.com/modern-route-optimization-with-python-fea87d34288b)
- [Flask documentation](https://flask.palletsprojects.com/en/3.0.x/tutorial/)

Warning, the module is not finished yet. It is just a proof of concept.

## Installation
To install the module, you need to install the dependencies with the following commands :
```bash
source .env/Scripts/activate
pip install -r requirements.txt
```

## Utilisation
To run the module, you need to run the following command :
```bash
python -m flask --app application run --debug
```

Warning, you need to be in the `routing-app` folder to run the module.
```bash
source .env/Scripts/activate
```

If everything went well, the following message should appear :
```bash
 * Serving Flask app "application"
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

As indicated, you can now go to the following address to access the module : [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

## Structure

Here's the skeleton of the module :
- `routing-app/`
  - `python_scripts/` : contains the python scripts
  - `static/` : contains the static files (css, js, ...)
  - `templates/` : contains the html files
  - `__init__.py` : the main file of the module

## Future updates
- [ ]  Implement the real estimated speed of the cyclist
- [ ]  Display the estimated elevation of the route
- [ ]  Add a search bar to search for a specific location
- [ ]  Add a button to center the map on the user's location
- [ ]  Add a button to center the map on the route
- [ ]  Allow the user to choose the type of route (fastest, shortest, ...)
- [ ]  Decrease the time to generate the route