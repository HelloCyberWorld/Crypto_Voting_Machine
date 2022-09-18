from . import constants


def initialise(key):

    P, S = constants.get_P(), constants.get_S() # permet de conserver P et S comme des constantes
    m = 0
    for i in range(len(P)): # On xor chaque bloc de P avec la clé k
        P[i] = int(P[i])
        P[i] ^= key[m]
        m = (m+1) % len(key)

    block = [0, 0]

    for i in range(0, len(P), 2): # chaque bloc de P est chiffré

        block = cipher(block, P, S)
        P[i] = block[0]
        P[i + 1] = block[1]

    for i in range(len(S)): # On chiffre aussi les blocs de S
        for j in range(0, len(S[0]), 2):
            block = cipher(block, P, S)
            S[i][j] = block[0]
            S[i][j + 1] = block[1]

    return P, S


def f(x, S): # fonction F utilisée dans les tournées de Feistel

    h = (S[0][x >> 24] + S[1][x >> 16 & 0xff]) % (2**32)

    h = ((h ^ S[2][x >> 8 & 0xff]) + S[3][x & 0xff]) % (2**32)

    return h


def cipher(list, P, S):

    ciphered = []
    L = list[0]
    R = list[1]

    for i in range(16): # 16 tournées de Feistel

        L = L ^ P[i]

        R = f(L, S) ^ R

        L, R = R, L  # swap

    L, R = R, L  # swap
    R = R ^ P[16]
    L = L ^ P[17]

    ciphered.append(L)
    ciphered.append(R)

    return ciphered


def decipher(cipher, P, S):
    deciphered = []
    L = cipher[0]
    R = cipher[1]

    for i in range(17, 1, -1):
        L = L ^ P[i]
        R = f(L, S) ^ R
        L, R = R, L  # swap

    L, R = R, L  # swap
    R = R ^ P[1]
    L = L ^ P[0]

    L = L.to_bytes(4, 'big')
    R = R.to_bytes(4, 'big')

    deciphered.append(L)
    deciphered.append(R)

    return deciphered


def padding(string): # comme on chiffre des blocs, on rajoute du padding nul pour obtenir la bonne taille

    while (len(string) % 8 != 0):
        string += ('\0')

    return string


def encrypt(data, key):

    while len(key) % 4 != 0: # padding sur la clé
        key += '\0'

    key = [key[i:i+4] for i in range(0, len(key), 4)]

    for j in range(len(key)):

        key[j] = bytes(key[j], 'utf8')
        key[j] = int.from_bytes(key[j], 'big')

    while(len(data) % 8 != 0):
        data += '\0'

    data = [data[i:i+8] for i in range(0, len(data), 8)]

    for j in range(len(data)):

        data[j] = [data[j][i:i+4] for i in range(0, len(data[j]), 4)]
        data[j][0] = int.from_bytes(bytes(data[j][0], 'utf8'), 'big')
        data[j][1] = int.from_bytes(bytes(data[j][1], 'utf8'), 'big')

    P, S = initialise(key)

    ciphered = []

    for block64 in data:

        ciphered.append(cipher(block64, P, S))

    return ciphered


def decrypt(ciphered, key):

    while len(key) % 4 != 0:
        key += '\0'

    key = [key[i:i+4] for i in range(0, len(key), 4)]

    for j in range(len(key)):

        key[j] = bytes(key[j], 'utf8')
        key[j] = int.from_bytes(key[j], 'big')

    plain = []

    P, S = initialise(key)

    for block64 in ciphered:

        plain.append(decipher(block64, P, S))

    ciphered_str = ""

    for chunk in plain:
        ciphered_str += (chunk[0].decode('utf8') + chunk[1].decode('utf8'))

    return ciphered_str

