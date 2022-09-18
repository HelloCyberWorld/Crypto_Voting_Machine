from .sha1 import sha1


import math

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

def F( P, S, c, i):
    key = P
    salt = S

    i = i.to_bytes(4, 'big') #block index
    
    message =  salt + i

    hmac_output  = hmac_sha1(key, message)

    if c == 1:
        return hmac_output

    xor_sum = int.from_bytes(hmac_output, 'big')

    for i in range(1, c):

        hmac_output = hmac_sha1(key, hmac_output)
        xor_sum ^= int.from_bytes(hmac_output, 'big')

    return xor_sum.to_bytes(20,'big')




def pbkdf2(password, salt, nb_itération, output_key_size):


    salt = bytes(salt, 'utf8')
    password = bytes(password, 'utf8')

    l = math.ceil(output_key_size / 20)

    result = bytes()

    for i in range(1, l+1):
        result+=F(password, salt, nb_itération, i)

   
    return result




