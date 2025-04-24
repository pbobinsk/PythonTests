import os
import requests # Do wykonywania zapytań HTTP
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

NODE_API_URL = os.getenv("NODE_API_URL", "http://127.0.0.1:3000/api/data")

# Adres URL serwisu Node.js - używamy nazwy serwisu z docker-compose.yml
# Docker Compose zapewni resolucję tej nazwy na odpowiedni adres IP w sieci Dockerowej.
# ręcznie
# NODE_API_URL = "http://127.0.0.1:3000/api/data"
# oddzielne kontenery
# NODE_API_URL = "http://moje-api:3000/api/data"
# Sieć docker Compose
# NODE_API_URL = "http://node_api_service:3000/api/data"


@app.route('/')
def index():
    wiadomosc_z_node = "Nie udało się połączyć z serwisem Node.js :("
    try:
        # Wykonaj zapytanie GET do serwisu Node.js
        response = requests.get(NODE_API_URL, timeout=5) # timeout na 5 sekund
        response.raise_for_status() # Rzuć wyjątek dla błędnych statusów HTTP (4xx, 5xx)

        # Odczytaj dane JSON z odpowiedzi
        data = response.json()
        wiadomosc_z_node = data.get('wiadomosc', 'Brak wiadomości w odpowiedzi JSON.')

    except requests.exceptions.ConnectionError:
        wiadomosc_z_node = f"Błąd połączenia z {NODE_API_URL}. Czy serwis Node.js działa?"
    except requests.exceptions.Timeout:
        wiadomosc_z_node = f"Przekroczono czas oczekiwania na odpowiedź z {NODE_API_URL}."
    except requests.exceptions.RequestException as e:
        wiadomosc_z_node = f"Wystąpił błąd zapytania do serwisu Node.js: {e}"
    except Exception as e:
         wiadomosc_z_node = f"Wystąpił nieoczekiwany błąd: {e}"


    # Prosty szablon HTML wyświetlający wiadomość
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Aplikacja Python + Node.js</title>
        <style>
            body { font-family: sans-serif; background-color: #f0f0f0; padding: 20px; }
            .container { background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            h1 { color: #333; }
            p { color: #555; font-size: 1.1em; }
            .node-message { background-color: #e7f3fe; border-left: 6px solid #2196F3; padding: 15px; margin-top: 15px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Witaj w aplikacji webowej Python (Flask)!</h1>
            <p>Poniżej wiadomość pobrana z serwisu Node.js:</p>
            <div class="node-message">
                <strong>{{ wiadomosc }}</strong>
            </div>
            <div class="node-message">
                <strong>To jest nowa wersja{{ wiadomosc }}</strong>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, wiadomosc=wiadomosc_z_node)

if __name__ == '__main__':
    # Uruchom aplikację Flask, nasłuchując na wszystkich interfejsach ('0.0.0.0')
    # na porcie 5000, aby była dostępna z zewnątrz kontenera.
    # testy CRASH w Swarm !!!
    # raise Exception("Błąd krytyczny!")
    # !!!

    app.run(host='0.0.0.0', port=5000, debug=True) # debug=True dla łatwiejszego rozwoju