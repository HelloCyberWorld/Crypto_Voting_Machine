from crypto.certificates import checking_certificate
from crypto.credentials import generate_credential
from crypto.pbkdf2 import pbkdf2
from crypto.blowfish import decrypt
from crypto.utils import fast_exponentiation
from crypto.sha1 import sha1, to_hex
from crypto.elgamal import generate_generator,encrypt_list_of_vectors, compute_chal_resp_sign

import random
import json


class Voter:
    
    def __init__(self, first_name, last_name, email):
        self._firstName = first_name
        self._lastName = last_name
        self._email = email

        self._blowfish_key = ""
        self._credential = ""
        self._ballot = ""
        self._ballot_hash = ""

    def download_and_check_certificate(self, server):

        print(self._firstName, " is checking a certificate ...")

        server_cert = server.get_certificate()
        ca_cert = self._ca_server.get_certificate()

        if checking_certificate(server_cert, ca_cert):

            return True

        else:
            return False


    def generate_blowfish_key(self):

        print(self._firstName, " is generating a blowfish key ...")

        salt = "salt"
        password = generate_credential(22)
        key = pbkdf2(password, salt, 1000, 30)
        key = int.from_bytes(key, 'big')
   
        self._blowfish_key = str(key)

    def download_voting_data(self, S_server):

        self._voting_data = S_server.get_voting_data()

    def download_election_parameters(self, server):

        self._election_parameters = server.get_election_parameters()

    
    def download_global_key(self, S_server):

        self._global_key = S_server.get_global_key()

    def cipher_and_send_blowfish_key(self, E_server):

        print(self._firstName, " is encrypting and sending th blowfish key ...")

        if self.download_and_check_certificate(E_server):

            cert = E_server.get_certificate()

            p = cert["request"]["large_prime"]
            g = cert["request"]["generator"]
            pub = cert["request"]["public_key"]
            key = int(self._blowfish_key)

            y = random.randint(2, p-1)
            c1 = fast_exponentiation(g, y, p)
            s = fast_exponentiation(pub, y, p)
            c2 = (key * s) % p

            E_server.add_blowfish_key(c2, c1)



    def set_uuid(self, uuid):
        self._uuid = uuid

    def set_credential(self, ciphered_credential):

        self._credential = decrypt(ciphered_credential, self._blowfish_key)

    def recompute_elgamal_keys(self):
        print(self._firstName,"is recomputing his private and public keys with th received credential")
        large_prime = self._election_parameters["large_prime"]
        generator = self._election_parameters["generator"]
        salt = self._election_parameters["id"]
        s_bytes = pbkdf2(self._credential, salt, 1000, 30)
        s = int.from_bytes(s_bytes, 'big')
        self._private_key = s
        self._public_key = fast_exponentiation(generator, s, large_prime)

    def set_ca_server(self, CA_server):

        self._ca_server = CA_server

    def voting_server_connection(self, S_server):

        if self.download_and_check_certificate(S_server):

            self.download_voting_data(S_server)
            self.download_election_parameters(S_server)
            self.download_global_key(S_server)

        else:

            print("Voting server certificate has been refused")

    def make_a_choice(self, S_server):

        ballot_vide = self._voting_data

        list_of_vectors = []

        type = ballot_vide["type"]

        questions = ballot_vide["questions"]

        print("le nom de l'élection est : " + ballot_vide["nom"])

        if type == 1:

            print("vous ne pouvez faire qu'un seul choix par question")

            for question in questions:

                print(question["question"])
                i = 1
                for reponse in question["reponses"]:
                    print(i, " : ", reponse)
                    i += 1
                i = 1
                choix = input("entrez le numéro associé à votre choix : ")

                allowed_choices = [str(x + 1) for x in range(len(question["reponses"]))]

                null_vector = []

                null_vector = [0] * len(question["reponses"])

                null_vector[int(choix) - 1] = 1

                while (choix not in allowed_choices):

                    print("please, enter a valid input")

                    choix = input("entrez le numéro associé à votre choix : ")

                    null_vector = [0] * len(question["reponses"])

                    null_vector[ int(choix) - 1] = 1

                list_of_vectors.append(null_vector)

        else :

            for question in questions:

                print(question["question"])

                tmp_lst = []

                i = 0
                while len(tmp_lst) < len(question["reponses"]):

                    choice = input("which position do you want to give to " + question["reponses"][i] + " : ")

                    allowed_choices = [str(x + 1) for x in range(len(question["reponses"]))]

                    while (choice not in allowed_choices) or (int(choice) in tmp_lst):
                        print("please, enter a valid input")
                        choice = input("which position do you want to give to " + question["reponses"][i] + " : ")

                    tmp_lst.append(int(choice))

                    i += 1

                list_of_vectors.append(tmp_lst)




        return list_of_vectors

    
    def send_ballot(self, ballot, S_server):

        if S_server.check_and_add_ballot(ballot):

            ballot_string = json.dumps(ballot)
            ballot_bytes = bytes(ballot_string, 'utf8')
            hashed_ballot = sha1(ballot_bytes)

            self._ballot = ballot
            self._ballot_hash = to_hex(hashed_ballot)

        else:

            print("the sending has failed")

    def vote(self, S_server):

        self.voting_server_connection(S_server)

        election_id = self._election_parameters["id"]
        large_prime = self._election_parameters["large_prime"]
        generator = self._election_parameters["generator"]

        list_of_vectors = self.make_a_choice(S_server)

        encrypted_list_of_vectors = encrypt_list_of_vectors(
            list_of_vectors,
            large_prime,
            generator,
            self._global_key)

        proof = compute_chal_resp_sign(
            large_prime,
            generator,
            encrypted_list_of_vectors,
            self._private_key)

        ballot = {"election_id": election_id, "votant_id": self._uuid, "voter_public_key": self._public_key,
                  "ciphered_choices": encrypted_list_of_vectors, "proof": proof}

        self.send_ballot(ballot, S_server)
    
    def __str__(self):
        return self._firstName + " ; " + self._lastName + " ; " + self._email 

    def get_first_name(self):
        return self._firstName

    def get_last_name(self):
        return self._lastName

    def get_email(self):
        return self._email

    def get_credential(self):
        return self._credential
    
    def get_uuid(self):
        return self._uuid

    def get_ballot(self):
        return self._ballot

    def get_ballot_hash(self):
        return self._ballot_hash