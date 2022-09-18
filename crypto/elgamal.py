from .primes import get_safe_prime
from .utils import fast_exponentiation, gcd, modular_inverse
from .credentials import generate_credential
from .sha1 import sha1
import random
import json
from .pbkdf2 import pbkdf2
import time

SIZE = 512

PRIVATE_KEY_SIZE = 30


"""Génération des clés"""

def generate_large_safe_prime(SIZE):
    time1 = time.time()
    print("generating a safe prime of ", SIZE, "bits ...")
    safe_prime = get_safe_prime(SIZE)
    time2 = time.time()
    diff = (time2 - time1) 
    print("took", diff, "seconds")
    return safe_prime

def generate_generator(large_safe_prime):
    p = large_safe_prime
    q = (p-1) // 2
    g = 2
    while( fast_exponentiation(g, 2, p) == 1 or fast_exponentiation(g, q, p) == 1 ): # on utilise le fait que p est un un entier fortement premier pour trouver un générateur
      g+=1  
    return g

def generate_private_key(size_in_bytes = PRIVATE_KEY_SIZE):

    password = generate_credential(22)
    salt = "salt"
    private_key = pbkdf2(password, salt, 1000, size_in_bytes)  
    
    private_key = int.from_bytes(private_key, 'big')
    
    return private_key


def generate_public_key(large_prime, generator, private_key):
    public_key = fast_exponentiation(generator, private_key, large_prime)

    return public_key

def signature(message, p, g, priv):

    message_string = json.dumps(message)
    message_bytes = bytes(message_string, 'utf8')
    h = sha1(message_bytes) # request doit être en bytes 
    h = int.from_bytes(h, 'big')

    k = random.randint(2, p-2)
    s = 0

    while ( s == 0 ):

        while ( gcd(k,p-1) != 1 ): # k doit être premier avec (p-1)

            k = random.randint(2, p-2)
  
        r = fast_exponentiation(g, k, p)

        inv_k = modular_inverse(k, p-1) # calcul d'inverse de k modulo p-1

        s = ( (h - priv*r)*inv_k ) % (p-1)


    return {"r" : r, "s" : s}

def check_signature(message, signature, p, g, pub):

    r = signature["r"]
    s = signature["s"]

    
    message_string = json.dumps(message)
    message_bytes = bytes(message_string, 'utf8')
    h = sha1(message_bytes)
    h = int.from_bytes(h, 'big')

   

    if ( ( 0 < r < p) and ( 0 < s < p - 1) ):

            premier_terme = fast_exponentiation(g, h, p) 

            deuxieme_terme = ( (fast_exponentiation(pub, r, p) * fast_exponentiation(r, s, p)) ) % p 

            if ( premier_terme == deuxieme_terme ):

                return True
    
    return False

def compute_chal_resp_sign(p, g, message, priv):

    proof = {}
    
    w = random.randint(2, p-1)

    A = fast_exponentiation(g, w, p)

    M = json.dumps(message)
    S = signature(M, p, g, priv)

    h1 = bytes(M, 'utf8')

    S1 = json.dumps(S)
    h2 = bytes(S1, 'utf8')

    A = str(A)
    h3 = bytes(A, 'utf8')

    to_hash = h1 + h2 + h3

    chal = int.from_bytes(sha1(to_hash), 'big')

    resp = (w - priv * chal ) % p

    proof["challenge"] = chal
    proof["response"] = resp
    proof["signature"] = S

    return proof


def check_knowledge(p, g, message, proof, pub):
    
    chal = proof["challenge"]
    resp = proof["response"]
    
    S = proof["signature"]

    A = ( fast_exponentiation(g, resp, p) * fast_exponentiation(pub, chal, p) ) % p

    M = json.dumps(message)
    h1 = bytes(M, 'utf8')
    
    S1 = json.dumps(S)
    h2 = bytes(S1, 'utf8')
    
    A = str(A)
    h3 = bytes(A, 'utf8')

    to_hash = h1 + h2 + h3

    chal_computed = int.from_bytes(sha1(to_hash), 'big')

    if chal_computed == chal:

        return True
    else:
        return False

def encrypt_list_of_vectors(list_of_vectors, p, g, pub): # chiffrement des vecteurs choix composant le bulletin de vote

    encrypted_list_of_vectors = []

    for vector in list_of_vectors:

        new_vector = []

        for value in vector:

            r = random.randint(2, p-1)

            while gcd(r, p) != 1:

                r = random.randint(2, p-1)

            alpha = fast_exponentiation(g, r, p)

            g_m = fast_exponentiation(g, value, p)

            beta = (fast_exponentiation(pub, r, p) *
                    g_m) % p

            encrypted_value = [alpha, beta]

            new_vector.append(encrypted_value)

        encrypted_list_of_vectors.append(new_vector)

    return encrypted_list_of_vectors

def solve_discrete_log(g_m, g, p, max_possible_value):

    for i in range(max_possible_value):

        if fast_exponentiation(g, i, p) == g_m:

            return i

    print("No value was found for the discrete log resolution in elgamal deciphering")


def decrypt_list_of_vectors(ciphered_list_of_vectors, g, p, priv): # déchiffrement des vecteurs choix composant le bulletin de vote

    plain_list_of_vectors = []

    for ciphered_vector in ciphered_list_of_vectors:

        plain_vector = []

        max_possible_value = len(ciphered_vector) + 1  # valeur max a tester pour la résolution du log discret
        for ciphered_value in ciphered_vector:

            alpha = ciphered_value[0]
            beta = ciphered_value[1]

            s = (fast_exponentiation(alpha, priv, p)) % p

            g_m_deciphered = (beta * modular_inverse(s, p)) % p

            m_deciphered = solve_discrete_log(g_m_deciphered, g, p, max_possible_value)
            plain_vector.append(m_deciphered)

        plain_list_of_vectors.append((plain_vector))

    return plain_list_of_vectors



