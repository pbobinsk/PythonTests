import jwt

from cryptography.hazmat.primitives import serialization


public_key = open('../../.ssh/id_rsa.pub', 'r').read()
key = serialization.load_ssh_public_key(public_key.encode())

token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MjQyIiwibmFtZSI6Ikplc3NpY2EgVGVtcG9yYWwiLCJuaWNrbmFtZSI6Ikplc3MifQ.qvlzCMTp0xOOuvmaaqMdSapW1bBzgHJo9U8Iid8eh08pQKed62D4_OT8zg6Ih1vCHBoOXZgfkjKy9S1970yfadVAuDRwYO2CdXa5eaeQ-5DoCzqo6txJ15KYY4VVvI5CprMEA0j5Lmh1ep3LHMl-0qzdLT_x_tpVFJF1w2e08-WnZkDZvdFfMrqhBYt39aOt520lnd4LVfdIT3Wd7v9achA3IJD4HmxrlnPsgmAfWe9CGeHH2tzId-uyjfS5JIp5xImY5w4bdiPlou9G52pYpuY50ef5c2ni_7O3vNB5m5kkvIGUcFljOj5Os0F8RPlqL7Krr4fCU73OqVRDr_07jcmnca5x6ZeY-N1ZZfvwm7EwcgOprwzsU5tlzhrZBWIJF35Wd9nKJMFDEMs8v0CavGM3AKwVpCuXV6ffIiXmDBFDNiRxJnVoPLmuM_lF9reZlTsrMZ6G5OQ44QPfCzVK94F--NQbLFWvugIr4PJB9cDX0I09gW-XwnWG6wuflS_G'
header_data = jwt.get_unverified_header(token)

payload_data = jwt.decode(jwt=token, key=public_key, algorithms=[header_data['alg'], ])
print('header: ', header_data)
print('payload: ', payload_data)