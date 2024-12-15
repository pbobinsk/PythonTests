from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Funkcje wczytujące klucze
def load_private_key(file_path, password=None):
    with open(file_path, "rb") as key_file:
        return serialization.load_pem_private_key(
            key_file.read(),
            password=password,
            backend=default_backend()
        )

def load_public_key(file_path):
    with open(file_path, "rb") as key_file:
        return serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )

# Wczytanie kluczy
private_key = load_private_key("./.keys/private_key_pkcs8.pem")
public_key = load_public_key("./.keys/public_key_x509.pem")

# Dane do podpisania
data = b"To jest wiadomosc do podpisania."

# Podpisanie danych
signature = private_key.sign(
    data,
    padding.PKCS1v15(),
    hashes.SHA256()
)

print("Podpis:", signature)

# Weryfikacja podpisu
try:
    public_key.verify(
        signature,
        data,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    print("Podpis jest prawidłowy!")
except Exception as e:
    print("Podpis nieprawidłowy:", e)
