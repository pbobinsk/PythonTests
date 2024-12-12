import jwt


token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MjQyIiwibmFtZSI6Ikplc3NpY2EgVGVtcG9yYWwiLCJuaWNrbmFtZSI6Ikplc3MiLCJleHAiOjE3MzM5OTcwNTV9.m5JAHW0kDFYeSsKNMTCqfNwICKS33SBpohvS08AHsQ4'

secret = 'my_super_secret'
header_data = jwt.get_unverified_header(token)

payload_data = jwt.decode(
    token,
    key=secret,
    algorithms=[header_data['alg'], ]
)
print(payload_data)