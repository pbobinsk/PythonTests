import requests

URL = "http://127.0.0.1:5000/graphql"

def execute_query(query):
    response = requests.post(URL, json={"query": query})
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Query failed: {response.status_code}, {response.text}")

if __name__ == "__main__":
    # Dodanie użytkownika (mutacja)
    create_user_mutation = """
    mutation {
        createUser(name: "Alice", email: "alice@example.com") {
            user {
                name
                email
            }
        }
    }
    """
    print("Create User Mutation:")
    print(execute_query(create_user_mutation))

    # Pobranie listy użytkowników (zapytanie)
    get_users_query = """
    {
        users {
            name
            email
        }
    }
    """
    print("\nUsers Query:")
    print(execute_query(get_users_query))
