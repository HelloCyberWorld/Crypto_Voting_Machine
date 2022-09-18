import json
import random

from .voter import Voter
from crypto.utils import fast_exponentiation
from crypto.elgamal import generate_private_key, generate_public_key, check_knowledge, check_signature


class Trustee(Voter):

    def __init__(self, first_name, last_name, email):
        
        super().__init__(first_name, last_name, email)

    def generate_keys(self):
        print(self.get_first_name(), "is generating private and public keys ...")
        self._large_prime = self._election_parameters["large_prime"]
        self._generator = self._election_parameters["generator"]
        self._private_key = generate_private_key()

        self._public_key = generate_public_key(
            self._large_prime,
            self._generator,
            self._private_key)

    def get_public_key(self):

        return self._public_key

    def check_ballot(self, ballot, pubs):

        generator = self._election_parameters["generator"]
        large_prime = self._election_parameters["large_prime"]
        voter_public_key = ballot["voter_public_key"] 
     
        vector = ballot["ciphered_choices"]
        proof = ballot["proof"]
        signature = proof["signature"]
        is_in_list = (voter_public_key in pubs)
        vector_string = json.dumps(vector)

        good_signature = check_signature(vector_string, signature, large_prime, generator, voter_public_key )
        knows_private_key = check_knowledge(large_prime, generator, vector, proof, voter_public_key)

        if (is_in_list and knows_private_key and good_signature):
            
            print("the ballot is fine")
            return True
        else :
            
            print("the ballot is wrong")
            return False

    def audit(self, S, A):
        
        print(self._firstName, " is checking ", A._name, " certificate")
        print(self.download_and_check_certificate(A))
        print(self._firstName, " is checking ", S._name, " certificate")
        print(self.download_and_check_certificate(S))

        self._election_parameters = S.get_election_parameters()

        print(self._firstName, " is auditing the vote ")
        ballots = S.get_ballots()

        pubs = A.get_pubs()

        pubs_so_far = []

        for ballot in ballots:

            
            if ( self.check_ballot(ballot, pubs) == False):
                return False
            public_key = ballot["voter_public_key"]
            if (public_key in pubs_so_far):
                print("a voter has voted multiple times")
                return False
            pubs_so_far.append(public_key)

        return True
    
    def cipher_and_send_private_key(self, server):

        if self.download_and_check_certificate(server):

            cert = server.get_certificate()
            p = cert["request"]["large_prime"]
            g = cert["request"]["generator"]
            pub = cert["request"]["public_key"]
            key = self._private_key

            y = random.randint(2, p-1)
            c1 = fast_exponentiation(g, y, p)
            s = fast_exponentiation(pub, y, p)
            c2 = (key * s) % p

            server.add_trustee_private_key(c2, c1)




