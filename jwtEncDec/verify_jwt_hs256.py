import jwt


token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MjQyIiwibmFtZSI6Ikplc3NpY2EgVGVtcG9yYWwiLCJuaWNrbmFtZSI6Ikplc3MiLCJleHAiOjE3MzM5OTA5OTB9.4_4ZnhA0qNKx_kCWuMTwfkcfMf2WA2V2mLE2a85xzv0'

secret = 'my_super_secret'
header_data = jwt.get_unverified_header(token)

payload_data = jwt.decode(
    token,
    key=secret,
    algorithms=[header_data['alg'], ]
)
print(payload_data)