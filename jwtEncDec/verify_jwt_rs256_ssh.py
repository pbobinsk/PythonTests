import jwt

from cryptography.hazmat.primitives import serialization

#public_key = open('./.keys/is_rsa.pub', 'r').read()
public_key = open('./.keys/public_key_x509.pem', 'rb').read()
#key = serialization.load_ssh_public_key(public_key.encode())
key = serialization.load_pem_public_key(public_key)

#token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MjQyIiwibmFtZSI6Ikplc3NpY2EgVGVtcG9yYWwiLCJuaWNrbmFtZSI6Ikplc3MifQ.qvlzCMTp0xOOuvmaaqMdSapW1bBzgHJo9U8Iid8eh08pQKed62D4_OT8zg6Ih1vCHBoOXZgfkjKy9S1970yfadVAuDRwYO2CdXa5eaeQ-5DoCzqo6txJ15KYY4VVvI5CprMEA0j5Lmh1ep3LHMl-0qzdLT_x_tpVFJF1w2e08-WnZkDZvdFfMrqhBYt39aOt520lnd4LVfdIT3Wd7v9achA3IJD4HmxrlnPsgmAfWe9CGeHH2tzId-uyjfS5JIp5xImY5w4bdiPlou9G52pYpuY50ef5c2ni_7O3vNB5m5kkvIGUcFljOj5Os0F8RPlqL7Krr4fCU73OqVRDr_07jcmnca5x6ZeY-N1ZZfvwm7EwcgOprwzsU5tlzhrZBWIJF35Wd9nKJMFDEMs8v0CavGM3AKwVpCuXV6ffIiXmDBFDNiRxJnVoPLmuM_lF9reZlTsrMZ6G5OQ44QPfCzVK94F--NQbLFWvugIr4PJB9cDX0I09gW-XwnWG6wuflS_G'
token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MjQyIiwibmFtZSI6Ikplc3NpY2EgVGVtcG9yYWwiLCJuaWNrbmFtZSI6Ikplc3MifQ.lg0vHUoP32RN-9m0u4-R2f8ln6_vyM_CCZ0IPQZKVrJd1WfWGfDW5byTe56A45yu7tDvYgwPvLVIosMuBSxVd_jdim5EAxOSKuebvnT0KSIguoHn3qBsCNsG2Qpt9SLYlUpRgbaCAye-SYRnK7SWxOLEjw0mBVrRLFk207UUDuqZigWJc_P0p6EQMca8JhDRftZeACGuPkAkC6_ZrOEmwfdJppV-tJyqM3tdOyDmWHd1ms6v6Lqv9V2b47HJLHwL8oeOJyV_oq6tyOUpHYYU69aNrWTKS1PTyvLWGE5HbH16yoW8Vd6qkP5UXUi7P2R8ZpATFMXQTmOfWX8BONPJ9Q'

header_data = jwt.get_unverified_header(token)

payload_data = jwt.decode(jwt=token, key=public_key, algorithms=[header_data['alg'], ])
print('header: ', header_data)
print('payload: ', payload_data)