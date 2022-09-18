from .sha1 import sha1


def hmac_sha1(key, message):

    key_length = len(key)

    if key_length > 64:
        key = sha1(key)
    
    if key_length < 64:
        while len(key) < 64:
            key+=b'\x00'

    #print("key = ",key, len(key))

    ipad = b'\x36' * 64 # ipad should be 0x36

    #print("ipad = ",ipad)

    opad = b'\x5c' * 64 # opad should be 0x5c

    #print("opad = ",opad)

    ipad_xored = int.from_bytes(key, byteorder="big") ^ int.from_bytes(ipad, 'big')
    opad_xored = int.from_bytes(key, byteorder="big") ^ int.from_bytes(opad, 'big')

    ipad_xored = int.to_bytes(ipad_xored, length=64, byteorder="big")
    opad_xored = int.to_bytes(opad_xored, length=64, byteorder="big")

    #print("ipad après xor avec la clé= ",ipad_xored)
    #print("opad après xor avec la clé= ",opad_xored)

    #print("ipad concaténé avec le message ",(ipad_xored + message))

    first_hash = sha1(ipad_xored + message)

    #print("le premier hash ",first_hash)

    #print("le premier hash en hex",toHex(first_hash))

    #print("opad concaténé avec le permier hash",opad_xored + first_hash)


    last_hash = sha1(opad_xored+first_hash)

    #print("le dernier hash ",last_hash)

    #print("le dernier hash en hex",toHex(last_hash))

    return last_hash



