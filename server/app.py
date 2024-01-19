#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        try:
            data = request.get_json()
            new_user = User(
                username = data["username"],
                image_url = data["image_url"],
                bio = data["bio"]
            )
            new_user.password_hash = data["password"]
            db.session.add(new_user)
            db.session.commit()
            session["user_id"] = new_user.id
            return new_user.to_dict(), 201
        except:
            return {"error": "failure to sign up"}, 422


class CheckSession(Resource):
    def get(self):
        if session["user_id"]:
            user = User.query.filter(User.id == session["user_id"]).first()
            return user.to_dict(), 200
        else:
            return {"Error": "unauthorized"}, 401

class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter(User.username == data.get("username")).first()
        if user:
        
            password = data["password"]

            if user.authenticate(password):
                session["user_id"] = user.id
                return user.to_dict(), 200

        return {"error": "invalid username or password"}, 401
        

#wasn't able to clear a key error about user_id, but the logout works
class Logout(Resource):
    def delete(self):
        if session["user_id"]:
            session["user_id"] = None
            return {}, 204

        return {"error": "not logged in"}, 401

            

        

class RecipeIndex(Resource):
    def get(self):
        if session["user_id"]:
            recipes = Recipe.query.filter(Recipe.user_id == session["user_id"]).all()
            rec_dict = []
            for each in recipes:
                rec_dict.append(each.to_dict())
            return rec_dict, 200
        else:
            return {"error": "unauthorized"}, 401
        
    def post(self):
        data = request.get_json()
        if session["user_id"]:
            try:
                new_recipe = Recipe(
                    title = data.get("title"),
                    instructions = data.get("instructions"),
                    minutes_to_complete = data.get("minutes_to_complete"),
                    user_id = session["user_id"]
                )
                db.session.add(new_recipe)
                db.session.commit()
                return new_recipe.to_dict(), 201
            except:
                return {"error": "validation errors"}, 422
        else:
            return {"error": "unauthorized"}, 401



        



api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)