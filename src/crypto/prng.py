import os
from math import log2, ceil

"""Values from the website 'asecurity.com', P and Q should be congruent to 3 mod 4 """

P = 30000000091
Q = 40000000003
M = 1200000003730000000273  # M = P * Q


def gcd(a, b):  # calcul du PGCD

    r0 = a
    r1 = b
    while (r1 != 0):
        r = r0 % r1
        if r == 0:
            return r1
        r0 = r1
        r1 = r


def generate_seed():   # on choisit une seed aléatoire de 64 bits et première avec M pour blum-blum-shub

    seed = int.from_bytes(os.urandom(4), 'big')

    while gcd(seed, M) != 1:

        seed = int.from_bytes(os.urandom(4), 'big')

    return seed


def get_parity(x):
    if x % 2 == 0:
        return 0
    else:
        return 1


def Blum_Blum_Shub(desired_bits_number):  # retourne une séquence de bits
    seed = generate_seed()
    random_sequence = []
    for i in range(desired_bits_number):
        seed = (seed**2) % M
        random_sequence.append(get_parity(seed))

    return random_sequence


def to_int(bit_list): # convertit une liste de bits en entier
    poids = 2**(len(bit_list)-1)
    res = 0
    for bit in bit_list:
        res += (bit*poids)
        poids //= 2
    return res


def get_random(bit_size):
    random_sequence = Blum_Blum_Shub(bit_size)
    random_int = to_int(random_sequence)
    return random_int


def get_random_in_range(a, b):

    bit_size = ceil(log2(b))
    random = get_random(bit_size)
    while not (a <= random <= b):
        random = get_random(bit_size)

    return random
