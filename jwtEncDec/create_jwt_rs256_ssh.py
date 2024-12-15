import jwt

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


payload_data = {
    'sub': '4242',
    'name': 'Jessica Temporal',
    'nickname': 'Jess'
}

# you'll need to create or update the path to correspond to an available key
#private_key = open('./.keys/id_rsa', 'r').read()
private_key = open('./.keys/private_key_pkcs8.pem', 'rb').read()
#key = serialization.load_ssh_private_key(private_key.encode(), password=b'qazxsw')
key = serialization.load_pem_private_key(private_key,password=None,backend=default_backend())

token = jwt.encode(payload=payload_data, key=key, algorithm='RS256')
print(token)