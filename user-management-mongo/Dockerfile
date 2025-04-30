# Użyj oficjalnego obrazu Python
FROM python:3.9-slim

# Ustaw katalog roboczy w kontenerze
WORKDIR /app

# Skopiuj plik zależności i zainstaluj je
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj resztę kodu aplikacji
COPY . .

# Ustaw zmienną środowiskową dla Flask (opcjonalne, ale dobra praktyka)
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
# Uwaga: MONGODB_URI będzie przekazane przez Docker Swarm, nie ustawiamy go tutaj na stałe

# Wystaw port, na którym działa Gunicorn
EXPOSE 5000

# Komenda uruchamiająca aplikację przez Gunicorn
# -b 0.0.0.0:5000 - nasłuchuj na wszystkich interfejsach na porcie 5000
# app:app - znajdź obiekt 'app' w pliku 'app.py'
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]