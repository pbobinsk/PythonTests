import os
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from bson import ObjectId # Do obsługi ID z MongoDB
import logging # Lepsze logowanie
import secrets # Do generowania sekretnego klucza, jeśli nie jest ustawiony
import datetime

from dotenv import load_dotenv # <--- IMPORT

load_dotenv() # <--- ZAŁADUJ zmienne z .env lub .flaskenv


# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# --- Klucz Sekretny dla Flash Messages ---
# W produkcji ZAWSZE ustawiaj to przez zmienną środowiskową!
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
if not app.config['SECRET_KEY']:
    logging.warning("SECRET_KEY nie znaleziono w środowisku! Używam tymczasowego.")
    app.config['SECRET_KEY'] = secrets.token_hex(16)


# --- Połączenie z MongoDB Atlas ---
MONGODB_URI = os.environ.get('MONGODB_URI')


if not MONGODB_URI:
    logging.error("Błąd: Zmienna środowiskowa MONGODB_URI nie jest ustawiona!")
    client = None
    db = None
    users_collection = None
else:
    try:
        client = MongoClient(MONGODB_URI)
        client.admin.command('ping')
        logging.info("Pomyślnie połączono z MongoDB Atlas!")
        db = client.get_database('usersdb') # Lub inna nazwa z URI
        users_collection = db.users
    except (ConnectionFailure, OperationFailure, Exception) as e:
        logging.error(f"Błąd podczas łączenia lub operacji na MongoDB: {e}")
        client = None
        db = None
        users_collection = None

# --- Funkcja pomocnicza sprawdzająca dostępność bazy ---
def check_db():
    # SPRAWDŹ, CZY ZMIENNA JEST None, a nie jej "prawdziwość"
    if users_collection is None: # <--- ZMIANA TUTAJ
        flash('Baza danych jest niedostępna.', 'error')
        # Logowanie błędu może być też przydatne tutaj, jeśli flash nie wystarczy
        logging.warning("Próba operacji na bazie danych, gdy users_collection jest None.")
        return False
    # Jeśli doszło tutaj, znaczy że users_collection nie jest None,
    # więc zakładamy, że połączenie zostało nawiązane poprawnie przy starcie.
    # Można by dodać dodatkowy ping do bazy dla pewności, ale może to spowolnić każde żądanie.
    return True


# --- PROCESOR KONTEKSTU DLA BIEŻĄCEGO ROKU ---
@app.context_processor
def inject_current_year():
    """Injects the current year into all templates."""
    return {'current_year': datetime.datetime.now().year,'db':MONGODB_URI}
# ---------------------------------------------


# --- API Endpoints (pozostają bez zmian dla ewentualnych innych klientów) ---

@app.route('/api/users', methods=['POST'])
def api_add_user():
    if not check_db(): return jsonify({"error": "Baza danych niedostępna"}), 500
    # ... (reszta logiki API POST jak poprzednio) ...
    # (dla zwięzłości pominięto kod API, jest taki sam jak poprzednio)
    try:
        data = request.get_json()
        if not data or 'name' not in data or 'email' not in data:
            return jsonify({"error": "Brak wymaganych pól 'name' i 'email'"}), 400
        if users_collection.find_one({"email": data['email']}):
             return jsonify({"error": "Użytkownik o tym emailu już istnieje"}), 409
        insert_result = users_collection.insert_one(data)
        return jsonify({"message": "User added", "id": str(insert_result.inserted_id)}), 201
    except Exception as e:
        logging.error(f"Błąd API podczas dodawania użytkownika: {e}")
        return jsonify({"error": "Wystąpił błąd serwera"}), 500


@app.route('/api/users', methods=['GET'])
def api_get_users():
    if not check_db(): return jsonify({"error": "Baza danych niedostępna"}), 500
    # ... (reszta logiki API GET all jak poprzednio) ...
    try:
        all_users = list(users_collection.find())
        for user in all_users: user['_id'] = str(user['_id'])
        return jsonify(all_users), 200
    except Exception as e:
        logging.error(f"Błąd API podczas pobierania użytkowników: {e}")
        return jsonify({"error": "Wystąpił błąd serwera"}), 500

@app.route('/api/users/<user_id>', methods=['GET'])
def api_get_user(user_id):
    if not check_db(): return jsonify({"error": "Baza danych niedostępna"}), 500
    # ... (reszta logiki API GET one jak poprzednio) ...
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            user['_id'] = str(user['_id'])
            return jsonify(user), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        logging.error(f"Błąd API podczas pobierania użytkownika {user_id}: {e}")
        return jsonify({"error": "Nieprawidłowy ID lub błąd serwera"}), 400


@app.route('/api/users/<user_id>', methods=['PUT'])
def api_update_user(user_id):
     if not check_db(): return jsonify({"error": "Baza danych niedostępna"}), 500
     # ... (reszta logiki API PUT jak poprzednio) ...
     try:
        data = request.get_json()
        if not data: return jsonify({"error": "Brak danych do aktualizacji"}), 400
        if 'email' in data:
             existing_user = users_collection.find_one({"email": data['email']})
             if existing_user and str(existing_user['_id']) != user_id:
                 return jsonify({"error": "Ten email jest już używany przez innego użytkownika"}), 409
        update_result = users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": data})
        if update_result.matched_count:
            return jsonify({"message": "User updated"}), 200
        else:
            return jsonify({"error": "User not found"}), 404
     except Exception as e:
        logging.error(f"Błąd API podczas aktualizacji użytkownika {user_id}: {e}")
        return jsonify({"error": "Nieprawidłowy ID lub błąd serwera"}), 400


@app.route('/api/users/<user_id>', methods=['DELETE'])
def api_delete_user(user_id):
     if not check_db(): return jsonify({"error": "Baza danych niedostępna"}), 500
     # ... (reszta logiki API DELETE jak poprzednio) ...
     try:
        delete_result = users_collection.delete_one({"_id": ObjectId(user_id)})
        if delete_result.deleted_count:
            return jsonify({"message": "User deleted"}), 200
        else:
            return jsonify({"error": "User not found"}), 404
     except Exception as e:
        logging.error(f"Błąd API podczas usuwania użytkownika {user_id}: {e}")
        return jsonify({"error": "Nieprawidłowy ID lub błąd serwera"}), 400


# --- Ścieżki dla interfejsu WEB (Jinja2) ---

@app.route('/')
def index():
    """Strona główna z linkami nawigacyjnymi."""
    return render_template('index.html')

@app.route('/users', methods=['GET'])
def list_users():
    """Wyświetla listę użytkowników."""
    if not check_db():
        # Renderuj szablon listy, ale przekaż informację o błędzie
        return render_template('list_users.html', users=[], db_error=True)

    try:
        all_users = list(users_collection.find())
        for user in all_users:
            user['_id'] = str(user['_id'])
        return render_template('list_users.html', users=all_users)
    except Exception as e:
        logging.error(f"Błąd podczas pobierania użytkowników dla widoku listy: {e}")
        flash('Wystąpił błąd podczas pobierania listy użytkowników.', 'error')
        return render_template('list_users.html', users=[], db_error=True)

@app.route('/users/add', methods=['GET', 'POST'])
def add_user():
    """Wyświetla formularz dodawania (GET) lub obsługuje dodanie (POST)."""
    if not check_db():
        # Jeśli GET, pokaż formularz z błędem; jeśli POST, przekieruj na listę (gdzie pojawi się błąd DB)
        if request.method == 'POST':
             return redirect(url_for('list_users'))
        else:
             # Można by stworzyć dedykowany szablon błędu lub przekazać flagę
             flash('Baza danych jest niedostępna, nie można dodać użytkownika.', 'error')
             return render_template('add_user.html') # Pokaż formularz, ale z błędem

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')

        if not name or not email:
            flash('Imię i email są wymagane.', 'error')
            # Pozostań na stronie formularza, aby użytkownik mógł poprawić
            return render_template('add_user.html', name=name, email=email)

        try:
            if users_collection.find_one({"email": email}):
                flash('Użytkownik o tym adresie email już istnieje.', 'warning')
                return render_template('add_user.html', name=name, email=email) # Zostań na formularzu
            else:
                users_collection.insert_one({'name': name, 'email': email})
                flash(f'Użytkownik {name} dodany pomyślnie.', 'success')
                return redirect(url_for('list_users')) # Przekieruj na listę po sukcesie
        except Exception as e:
            logging.error(f"Błąd web podczas dodawania użytkownika: {e}")
            flash('Wystąpił błąd serwera podczas dodawania użytkownika.', 'error')
            # Pozostań na stronie formularza w razie błędu serwera
            return render_template('add_user.html', name=name, email=email)

    # Metoda GET - po prostu wyświetl formularz
    return render_template('add_user.html')


@app.route('/users/edit/<user_id>', methods=['GET'])
def edit_user(user_id):
    """Wyświetla formularz edycji dla konkretnego użytkownika."""
    if not check_db():
        return redirect(url_for('list_users')) # Przekieruj na listę, tam będzie błąd DB

    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            user['_id'] = str(user['_id'])
            return render_template('edit_user.html', user=user)
        else:
            flash('Nie znaleziono użytkownika.', 'error')
            return redirect(url_for('list_users'))
    except Exception as e:
        logging.error(f"Błąd web podczas pobierania użytkownika do edycji {user_id}: {e}")
        flash('Wystąpił błąd podczas ładowania formularza edycji.', 'error')
        return redirect(url_for('list_users'))


@app.route('/users/update/<user_id>', methods=['POST'])
def update_user(user_id):
    """Obsługuje aktualizację użytkownika z formularza edycji."""
    if not check_db():
        return redirect(url_for('list_users'))

    name = request.form.get('name')
    email = request.form.get('email')

    # Podstawowa walidacja danych wejściowych
    if not name or not email:
        flash('Imię i email są wymagane.', 'error')
        # Przekieruj z powrotem do formularza edycji, aby użytkownik mógł poprawić
        # Trzeba by przekazać dane użytkownika ponownie lub pobrać je na nowo
        return redirect(url_for('edit_user', user_id=user_id))

    try:
        # Sprawdź unikalność emaila (pomijając samego siebie)
        existing_user = users_collection.find_one({"email": email})
        if existing_user and str(existing_user['_id']) != user_id:
             flash('Ten email jest już używany przez innego użytkownika.', 'warning')
             return redirect(url_for('edit_user', user_id=user_id)) # Wróć do edycji

        update_result = users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"name": name, "email": email}}
        )

        if update_result.matched_count:
            if update_result.modified_count:
                flash(f'Dane użytkownika {name} zaktualizowane.', 'success')
            else:
                flash('Nie wykryto żadnych zmian.', 'info')
        else:
             flash('Nie znaleziono użytkownika do aktualizacji.', 'error') # Błąd logiczny, ale na wszelki wypadek

    except Exception as e:
        logging.error(f"Błąd web podczas aktualizacji użytkownika {user_id}: {e}")
        flash('Wystąpił błąd serwera podczas aktualizacji.', 'error')
        return redirect(url_for('edit_user', user_id=user_id)) # Wróć do edycji w razie błędu serwera

    return redirect(url_for('list_users')) # Przekieruj na listę po sukcesie


@app.route('/users/delete/<user_id>', methods=['POST'])
def delete_user(user_id):
    """Obsługuje usuwanie użytkownika (tylko POST)."""
    if not check_db():
        return redirect(url_for('list_users'))

    # Sprawdzenie metody dla bezpieczeństwa, mimo że trasa dopuszcza tylko POST
    if request.method == 'POST':
        try:
            delete_result = users_collection.delete_one({"_id": ObjectId(user_id)})
            if delete_result.deleted_count:
                flash('Użytkownik usunięty.', 'success')
            else:
                flash('Nie znaleziono użytkownika do usunięcia.', 'error')
        except Exception as e:
            logging.error(f"Błąd web podczas usuwania użytkownika {user_id}: {e}")
            flash('Wystąpił błąd serwera podczas usuwania.', 'error')
    else:
        # Teoretycznie nieosiągalne przy poprawnym routingu, ale dla pewności
        flash('Nieprawidłowa metoda żądania.', 'error')


    return redirect(url_for('list_users'))


if __name__ == '__main__':
    # Uruchomienie przez Gunicorn będzie preferowane w Dockerze
    app.run(host='0.0.0.0', port=5000, debug=False)