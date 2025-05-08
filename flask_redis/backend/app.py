from flask import Flask, jsonify
from flask_cors import CORS # Do obsługi żądań z innego portu (frontend)
import redis
import requests
import time
import os

app = Flask(__name__)
CORS(app) # Umożliwia żądania z localhost:8080 (frontend) do localhost:5000 (backend)

# Konfiguracja połączenia z Redisem
# Używamy nazwy serwisu 'redis' z docker-compose.yml
redis_host = os.environ.get('REDIS_HOST', 'redis') # 'redis' to nazwa serwisu w docker-compose
redis_port = int(os.environ.get('REDIS_PORT', 6379))
try:
    r = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)
    r.ping()
    print("Połączono z Redis!")
except redis.exceptions.ConnectionError as e:
    print(f"Nie można połączyć się z Redis: {e}")
    # W prawdziwej aplikacji można by tu zastosować logikę fallback lub zakończyć działanie
    r = None


CACHE_EXPIRATION_SECONDS = 10 # Czas życia cache w sekundach
EXTERNAL_API_URL = "https://uselessfacts.jsph.pl/api/v2/facts/random"

@app.route('/api/fact', methods=['GET'])
def get_random_fact():
    if not r:
        return jsonify({"error": "Redis not available", "fact": "Could not fetch fact due to Redis connection error."}), 500

    cache_key = "random_fact"
    cached_fact = r.get(cache_key)

    if cached_fact:
        source = "cache"
        fact_text = cached_fact
        print(f"Zwracam fakt z cache: {fact_text[:30]}...")
    else:
        source = "API"
        print("Cache miss. Pobieram fakt z zewnętrznego API...")
        try:
            # Symulacja dłuższego zapytania (opcjonalnie, żeby lepiej zobaczyć różnicę)
            # time.sleep(2)
            response = requests.get(EXTERNAL_API_URL, timeout=5)
            response.raise_for_status() # Rzuci wyjątkiem dla złych statusów HTTP
            fact_data = response.json()
            fact_text = fact_data.get("text", "Nie udało się pobrać faktu.")

            # Zapisz do cache z czasem wygaśnięcia
            r.set(cache_key, fact_text, ex=CACHE_EXPIRATION_SECONDS)
            print(f"Zapisano fakt do cache: {fact_text[:30]}...")
        except requests.exceptions.RequestException as e:
            print(f"Błąd podczas pobierania faktu z API: {e}")
            return jsonify({"error": "Failed to fetch from external API", "fact": "Could not retrieve fact."}), 500
        except Exception as e:
            print(f"Nieoczekiwany błąd: {e}")
            return jsonify({"error": "Unexpected error", "fact": "An unexpected error occurred."}), 500


    return jsonify({
        "fact": fact_text,
        "source": source,
        "timestamp": time.time()
    })

@app.route('/')
def index():
    return "Flask backend działa! Spróbuj /api/fact"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)