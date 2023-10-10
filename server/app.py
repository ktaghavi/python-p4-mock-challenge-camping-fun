#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.get('/campers')
def get_all_campers():
    campers = Camper.query.all()
    data = [camper.to_dict(rules=('-signups',)) for camper in campers]
    return make_response(
        jsonify(data), 
        200
    )

@app.post('/campers')
def post_camper():
    data = request.get_json()

    try:
        new_camper = Camper(
            name=data.get('name'),
            age=data.get('age')
        )
        db.session.add(new_camper)
        db.session.commit()

        return make_response(
            jsonify(new_camper.to_dict(rules='-signups',)),
            201
        )
    except ValueError:
        return make_response(
            jsonify{"errors": ["validation errors"]},
            406
        )


@app.route('/campers/<int:id>')
def get_camper_by_id(id):
    campers = Camper.query.filter(Camper.id==id)first()

    if not camper:
        return make_response(
            jsonify({"error": "Camper not found"}),
            404
        )

    return make_response(
        jsonify(camper.to_dict()),
        200
    )

@app.patch('/campers/<int:id>')
def patch_camper_by_id(id):
    campers = Camper.query.filter(Camper.id==id)first()
    data = request.get_json()

    if not camper:
        return make_response(
            jsonify({"error": "Camper not found"}),
            404
        )

    try:
        for field in data:
            setattr(camper, field, data[field])
        db.session.add(camper)
        db.session.commit()
            
        return make_response(
            jsonify(camper.to_dict(rules=('-signup',))),
            202
        )
    except ValueError:
        return make_response(
            jsonify{"errors": ["validation errors"]},
            406
        )

@app.get('/activities')
def get_all_activities():
    activities = Activity.query.all()
    data = [activity.to_dict(rules=('-signups',)) for activity in activities]

    return make_response(
        jsonify(data),
        200
    )

@app.delete('/activities/<int:id>')
def delete_activity(id):
    activity = Activity.query.filter(Activity.id==id)first()

    if not activity:
        return make_response(
            jsonify({"error": ["validation errors"]}),
            406
        )

    db.session.delete(activity)
    db.session.commit()

    return make_response(jsonify({}), 204)

@app.post('/signups')
def post_signup():
    data = requests.get_json()

    try:
        new_signup = Signup(
            time=data.get('time'),
            camper_id=data.get('camper_id'),
            activity_id=data.get('activity_id')
        )
        db.session.add(new_signup)
        db.session.commit()

        return make_response(
            jsonify(new_signup.to_dict(rules=('activity', 'camper', '-activity.signups', '-camper.signups'))),
            201
        )

    except ValueError:
        return make_response(
            jsonify({"errors": ["validation errors"]}),
            406
        )

if __name__ == '__main__':
    app.run(port=5555, debug=True)
