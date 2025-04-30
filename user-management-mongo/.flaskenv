FLASK_APP=App.py
FLASK_DEBUG=1
FLASK_ENV=development  # Włącza tryb debugowania i automatyczne przeładowanie

SECRET_KEY='sekretny-klucz-tylko-dla-lokalnego-developmentu-zmien-mnie!'
# MONGODB_URI='mongodb+srv://<twoj_dev_user>:<twoje_dev_haslo>@<twoj_dev_klaster_atlas>/dev_db?retryWrites=true&w=majority'
MONGODB_URI='mongodb://localhost:27017/usersdb'