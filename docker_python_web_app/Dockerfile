# Użyj oficjalnego obrazu Python w wersji slim
FROM python:3.10-slim

# Ustaw katalog roboczy
WORKDIR /app

# Skopiuj plik zależności i zainstaluj je
# Kopiowanie najpierw requirements.txt pozwala wykorzystać cache warstw Dockera,
# jeśli plik się nie zmienił, nie trzeba ponownie instalować zależności.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj resztę kodu aplikacji
COPY app.py .

# Poinformuj Docker, że kontener będzie nasłuchiwał na porcie 5000
EXPOSE 5000

# Komenda do uruchomienia aplikacji Flask przy starcie kontenera
# Używamy gunicorn w przyszłości dla produkcji, ale dla przykładu wystarczy serwer deweloperski Flaska.
CMD ["python", "app.py"]