import json
from .prng import get_random_in_range
from . import sha1
from .utils import gcd, fast_exponentiation, modular_inverse



def generate_request(name, large_prime, generator, public_key):
    
    request  = {"name" : name, "large_prime" : large_prime, "generator" : generator, "public_key"  : public_key}

    return request 


def generate_self_signed_signature(request, priv):
        
    p = request["large_prime"]
    g = request["generator"]
    request_string = json.dumps(request)
    request_bytes = bytes(request_string, 'utf8')
    h = sha1.sha1(request_bytes) # request doit être en bytes 
    h = int.from_bytes(h, 'big')
  
    k = get_random_in_range(0, p-1)
    s = 0

   
    while ( s == 0 ):

        while ( gcd(k,p-1) != 1 ):

            k = get_random_in_range(2, p-2)
  
        r = fast_exponentiation(g, k, p)


        inv_k = modular_inverse(k, p-1)

        s = ( (h - priv*r)*inv_k ) % (p-1)

    return {"r" : r, "s" : s}

def generate_signature(request, priv, authority_certificate):
        
    p = authority_certificate["request"]["large_prime"]
    g = authority_certificate["request"]["generator"]
    

    request_string = json.dumps(request)
    request_bytes = bytes(request_string, 'utf8')

    h = sha1.sha1(request_bytes) # request doit être en bytes 

    h = int.from_bytes(h, 'big')
  
    k = get_random_in_range(0, p-1)
    s = 0

   
    while ( s == 0 ):

        while ( gcd(k,p-1) != 1 ):

            k = get_random_in_range(2, p-2)
  
        r = fast_exponentiation(g, k, p)


        inv_k = modular_inverse(k, p-1)

        s = ( (h - priv*r)*inv_k ) % (p-1)

    return {"r" : r, "s" : s}



def generate_certificate(name, p, g, pub, priv, authority_certificate):
    
    request = generate_request(name, p, g, pub)

    signature = generate_signature(request, priv, authority_certificate)

    certificate = {"request" : request, "signature" : signature}

    return certificate 


def generate_self_signed_certificate(name, p, g, pub, priv):
    
    request = generate_request(name, p, g, pub)


    signature = generate_self_signed_signature(request, priv)

    certificate = {"request" : request, "signature" : signature}

    return certificate 



def checking_certificate(server, authority):

    signature_server = server["signature"]
    request_server = server["request"]
    request_server_string = json.dumps(request_server)
    request_server_bytes = bytes(request_server_string, 'utf8')
    h = sha1.sha1(request_server_bytes)
    h = int.from_bytes(h, 'big')


    # signature issue du certificat du serveur
    r = signature_server["r"]
    s = signature_server["s"]

    # paramètres issues du certificat de l'autorité de certification
    p = authority["request"]["large_prime"]
    g = authority["request"]["generator"]
    pub = authority["request"]["public_key"]    


    if ( ( 0 < r < p) and ( 0 < s < p - 1) ):

             
            premier_terme = fast_exponentiation(g, h, p) 

 
            deuxieme_terme = ( (fast_exponentiation(pub, r, p) * fast_exponentiation(r, s, p)) ) % p 
        

            if ( premier_terme == deuxieme_terme ):
                return True
    
    return False




        


