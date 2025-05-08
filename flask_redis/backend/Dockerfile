# Użyj oficjalnego obrazu Python
FROM python:3.9-slim

# Ustaw katalog roboczy
WORKDIR /app

# Skopiuj plik z zależnościami
COPY requirements.txt .

# Zainstaluj zależności
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj resztę kodu aplikacji
COPY . .

# Ustaw zmienną środowiskową (opcjonalnie, bo mamy default w kodzie)
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379

# Uruchom aplikację
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]