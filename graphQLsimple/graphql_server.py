from flask import Flask, request, jsonify
from graphene import ObjectType, String, Schema, Field, Mutation, List
from flask_cors import CORS


# Prosta baza danych w pamięci
users = []

# Definicja obiektu User
class User(ObjectType):
    name = String()
    email = String()

# Zapytania (Queries)
class Query(ObjectType):
    users = List(User)

    def resolve_users(self, info):
        return users

# Mutacje (Mutations)
class CreateUser(Mutation):
    class Arguments:
        name = String(required=True)
        email = String(required=True)

    user = Field(User)

    def mutate(self, info, name, email):
        user = {"name": name, "email": email}
        users.append(user)
        return CreateUser(user=user)

class Mutation(ObjectType):
    create_user = CreateUser.Field()

# Schemat GraphQL
schema = Schema(query=Query, mutation=Mutation)

# Tworzenie serwera Flask
app = Flask(__name__)

CORS(app, resources={r"/graphql": {"origins": ["http://127.0.0.1:8000","http://localhost:8000"]}})

@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    result = schema.execute(data.get("query"))
    return jsonify(result.data)
