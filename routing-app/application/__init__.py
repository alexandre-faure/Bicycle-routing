'''
Initialize the app
'''

import os
from flask import Flask, render_template, request, jsonify
from .python_scripts import routing

# To run the app : source ./.env/Scripts/activate
# then : python -m flask --app application run --debug

def create_app():
    '''
    Create and configure the app
    '''
    app = Flask(__name__, instance_relative_config=True)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Main page
    @app.route('/')
    def hello():
        return render_template('index.html')
    
    # Route to calculate the road
    @app.route('/calculate_road', methods=['POST'])
    def calculate_routing():
        road_markers = request.get_json()  # Récupère le dictionnaire JSON de la requête POST
        #Par exemple, renvoyez-le en tant que réponse JSON

        return jsonify(routing.get_routing(road_markers.get('start'), road_markers.get('end')))

    return app