from .prng import get_random_in_range


def gcd(a, b):  # calcul de pgcd par division euclidienne
    r0 = a
    r1 = b
    while (r1 != 0):
        r = r0 % r1
        if r == 0:
            return r1
        r0 = r1
        r1 = r

def fast_exponentiation(a, e, m):

    result = 1
    while e > 0:
        if e % 2 == 1:
            result *= a % m

        a *= a % m
        e //= 2

    return result % m


def miller_witness(n, a, d, s):

    x = pow(a, d, n)

    if (x == 1 or x == (n-1)):

        return False

    for r in range(s-1):

        x = x**2 % n
        if x == n-1:
            return False

    return True


def rabin_miller(n, k=7):

    if n in [2, 3, 5, 7, 11, 13]:
        return True

    if n % 2 == 0 or n < 2:
        return False

    s = 1
    d = (n-1)

    while d % 2 == 0:
        s += 1
        d //= 2

    for _ in range(k):

        a = get_random_in_range(2, n-1)
        #a = random.randint(2, n-1)
        if (miller_witness(n, a, d, s)):

            return False

    return True


def modular_inverse(a, m): # calcul d'inverse par la méthode de Bezout
    
    s = 0; old_s = 1
    t = 1; old_t = 0
    r = m; old_r = a

    while r != 0:
      quotient = old_r//r 
      old_r, r = r, old_r - quotient*r
      old_s, s = s, old_s - quotient*s
      old_t, t = t, old_t - quotient*t

    return old_s % m

