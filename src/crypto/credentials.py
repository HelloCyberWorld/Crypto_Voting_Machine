from .prng import to_int, get_random


base_58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"



def generate_credential(size=14):
    credentials = []
    for i in range (0,size):
        random_number = get_random(64) % 58
        credentials.append(random_number)
    credentials = add_checksum(credentials)
    return(credential_toString(credentials))

def add_checksum(cred):
    checksum_bytes = bytes()
    for i in cred:
        checksum_bytes+=(i.to_bytes(1, 'big'))
    
    int_checksum = int.from_bytes(checksum_bytes, 'big')
    int_checksum = (53 - int_checksum) % 53

    cred.append(int_checksum)
    return cred

def credential_toString(credential):
    credential_string = ""
    for i in credential:
        credential_string+=base_58[i]

    return credential_string





