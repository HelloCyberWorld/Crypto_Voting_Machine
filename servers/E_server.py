from .Server import Server
import random
from crypto.credentials import generate_credential
from crypto.pbkdf2 import pbkdf2
from crypto.utils import fast_exponentiation, modular_inverse
from crypto.blowfish import encrypt



class E_server(Server):

    def __init__(self, voters, elgamal_parameters, election_parameters, ca_server):
        super().__init__(elgamal_parameters, election_parameters, ca_server)
        
        self._voters = voters
        self._credentials = []
        self._pubs = []
        self._blowfish_keys = []

    def generate_credentials_and_pub(self):

        for voter in self._voters:

            print("E_server is generating credential and pub for ", voter._firstName, " ...")

            credential = generate_credential(14)
            secret = self.generate_secret(credential)
            pub = self.generate_pub(secret)

            self._credentials.append(credential)
            self._pubs.append(pub)

        print()

    def generate_secret(self, credential):
        salt = self._election_parameters["id"]
        s_bytes = pbkdf2(credential, salt, 1000, 30)
        s = int.from_bytes(s_bytes, 'big')
        return s

    def generate_pub(self, secret):

        p = self._election_parameters["large_prime"]
        g = self._election_parameters["generator"]
        pub = fast_exponentiation(g, secret, p)
        return pub

    def add_blowfish_key(self, ciphered, shared_secret):

        s = fast_exponentiation(shared_secret, self._private_key, self._large_prime)
        plain_key  = ( ciphered * modular_inverse(s, self._large_prime)) % self._large_prime
        self._blowfish_keys.append(str(plain_key))
    
    def send_ciphered_credentials(self):

        for i in range(len(self._voters)):

            print("E_server is sending the ciphered credential to ", self._voters[i]._firstName)
            ciphered_credential = encrypt(self._credentials[i], self._blowfish_keys[i])
            self._voters[i].set_credential(ciphered_credential)

        print()

    def remove_credentials(self):

        self._credentials.clear()
    
    def remove_blowfish_keys(self):

        self._blowfish_keys.clear()

    def shuffle_pubs(self):
        random.shuffle(self._pubs)

    def sending_pubs(self, A):

        A.set_pubs(self._pubs)



