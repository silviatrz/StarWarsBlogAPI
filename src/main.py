"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Character_Fav, Planet_Fav
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/characters', methods=['GET'])
def listCharacters():
    list_characters = Character.query.all()
    return jsonify([character.serialize() for character in list_characters]), 200

@app.route('/characters/<int:character_id>', methods=['GET'])
def getCharacter(character_id):
    character = Character.query.filter_by(id=character_id).first()
    return jsonify(character.serialize()), 200

@app.route('/planets', methods=['GET'])
def listPlanets():
    list_planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in list_planets]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def getPlanet(planet_id):
    planet = Planet.query.filter_by(id=planet_id).first()
    return jsonify(planet.serialize()), 200

@app.route('/users', methods=['GET'])
def listUsers():
    list_users = User.query.all()
    return jsonify([user.serialize() for user in list_users]), 200

@app.route('/users/<int:user_id>', methods=['GET'])
def getUser(user_id):
    user = User.query.filter_by(id=user_id).first()
    return jsonify(user.serialize()), 200

@app.route('/users/favorites', methods=['GET'])
def listFavorites():
    characterFavs = Character_Fav.query.all()
    planetFavs = Planet_Fav.query.all()
    favs = [fav.serialize() for fav in characterFavs]
    favs += [fav.serialize() for fav in planetFavs]
    return jsonify(favs), 200

@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def listUserFavorites(user_id):
    characterFavs = Character_Fav.query.filter_by(id_user=user_id)
    planetFavs = Planet_Fav.query.filter_by(id_user=user_id)
    favs = [fav.serialize() for fav in characterFavs]
    favs += [fav.serialize() for fav in planetFavs]
    return jsonify(favs), 200

@app.route('/users/<int:user_id>/favorites/planets/<int:planet_id>', methods=['POST'])
def setUserPlanetFavorite(user_id, planet_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        raise APIException('User does not exist', status_code=404)
    planet = Planet.query.filter_by(id=planet_id).first()
    if planet is None:
        raise APIException('Planet does not exist', status_code=404)
    fav = Planet_Fav(id_user=user.id, id_planet=planet.id)
    db.session.add(fav)
    db.session.commit()
    return jsonify(fav.serialize()), 200

@app.route('/users/<int:user_id>/favorites/characters/<int:character_id>', methods=['POST'])
def setUserCharacterFavorite(user_id, character_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        raise APIException('User does not exist', status_code=404)
    character = Character.query.filter_by(id=character_id).first()
    if character is None:
        raise APIException('Character does not exist', status_code=404)
    fav = Character_Fav(id_user=user.id, id_character=character.id)
    db.session.add(fav)
    db.session.commit()
    return jsonify(fav.serialize()), 200

@app.route('/users/<int:user_id>/favorites/planets/<int:planet_id>', methods=['DELETE'])
def deleteUserPlanetFavorite(user_id, planet_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        raise APIException('User does not exist', status_code=404)
    fav = Planet_Fav.query.filter_by(id_user=user.id, id_planet=planet_id).first()
    if fav is None:
        raise APIException('Planet does not exist as favorite', status_code=404)
    db.session.delete(fav)
    db.session.commit()
    return "Planet deleted as favorite", 200

@app.route('/users/<int:user_id>/favorites/characters/<int:character_id>', methods=['DELETE'])
def deleteUserCharacterFavorite(user_id, character_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        raise APIException('User does not exist', status_code=404)
    fav = Character_Fav.query.filter_by(id_user=user.id, id_character=character_id).first()
    if fav is None:
        raise APIException('Character does not exist as favorite', status_code=404)
    db.session.delete(fav)
    db.session.commit()
    return "Character deleted as favorite", 200


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
