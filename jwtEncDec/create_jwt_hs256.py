import jwt
from datetime import date, datetime, timedelta

dt=datetime.utcnow()+timedelta(seconds=120)

print(dt)


payload_data = {
    'sub': '4242',
    'name': 'Jessica Temporal',
    'nickname': 'Jess',
    'exp':dt
}

secret = 'my_super_secret'
token = jwt.encode(payload=payload_data, key=secret)
print(token)

