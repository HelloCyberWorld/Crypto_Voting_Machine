from .prng import Blum_Blum_Shub, to_int
from .utils import rabin_miller

first_primes_list = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, # permet d'éviter de faire du rabin-miller trop souvent
                     31, 37, 41, 43, 47, 53, 59, 61, 67,
                     71, 73, 79, 83, 89, 97, 101, 103,
                     107, 109, 113, 127, 131, 137, 139,
                     149, 151, 157, 163, 167, 173, 179,
                     181, 191, 193, 197, 199, 211, 223,
                     227, 229, 233, 239, 241, 251, 257,
                     263, 269, 271, 277, 281, 283, 293,
                     307, 311, 313, 317, 331, 337, 347, 349]


def get_prime_candidate(size): # on génère un entier aléatoire impaire de n_bits = size
  candidate = Blum_Blum_Shub(size-2)
  candidate.append(1)
  candidate.insert(0, 1)
  return to_int(candidate)


def is_divisible_by_first_primes(x): # on test s'il est divisible par les premiers premiers pour gagner du temps dans rabin-miller
    for prime in first_primes_list:
        if(x % prime == 0):
            return True
    return False

def get_prime(size): # on choisit un entier impaire aléatoire et on test s'il est premier jusque obtenir un qui passe le test de rabin-miller

    candidate = get_prime_candidate(size)
    while rabin_miller(candidate) != True:
        candidate = get_prime_candidate(size)
        if (is_divisible_by_first_primes(candidate) == True):
            candidate = get_prime_candidate(size)
    return candidate

def get_safe_prime(size):
  
  q = get_prime(size-1)
  
  while(rabin_miller(2*q + 1) != True): # pour avoir un entier fortement premier, on vérifie que 2*q + 1 est aussi premier afin de simplifier le calcul du générateur notamment
    
    q = get_prime(size-1)

  return (2*q + 1)

