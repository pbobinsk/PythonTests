from bitcoin_field import PrivateKey, PublicKey
import hashlib


if __name__ == "__main__":

    M = 'Message for signing'
    h = int.from_bytes(hashlib.sha256(M.encode()).digest(), 'big')
    
    secret = 0x1A2B3C4D5E6F7890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890
    priv = PrivateKey(secret)
    signature = priv.sign(h)
    pub = PublicKey(priv.point)

    print("Signature")
    print(f"Podpis: (r={hex(signature.r)}, s={hex(signature.s)})")
    print(f'Podpis w DER: {signature.der()}')
 
    print("PrivateKey")
    print(f'Private Key repr: {priv}')
    print(f'Private Key hex: {priv.hex()}')
    print(f'Private Key wif c=T, t=F: {priv.wif()}')
    print(f'Private Key wif c=T, t=T: {priv.wif(testnet=True)}')
    print(f'Private Key wif c=F, t=F: {priv.wif(compressed=False)}')
    print(f'Private Key wif c=F, t=T: {priv.wif(compressed=False,testnet=True)}')

    print("PublicKey")
    print(f'Public Key repr: {pub}')
    print(f'Public Key sec c=T: {pub.point.sec()}')
    print(f'Public Key sec c=F: {pub.point.sec(compressed=False)}')
    print(f'Public Key address c=T, t=F: {pub.point.address()}')
    print(f'Public Key address c=F, t=F: {pub.point.address(compressed=False)}')
    print(f'Public Key address c=T, t=T: {pub.point.address(testnet=True)}')
    print(f'Public Key address c=F, t=T: {pub.point.address(compressed=False,testnet=True)}')

