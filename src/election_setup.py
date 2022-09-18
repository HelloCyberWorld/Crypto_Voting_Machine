import os
import json
import uuid
import paths

from crypto.elgamal import generate_large_safe_prime, generate_private_key, generate_public_key, generate_generator
from users.voter import Voter
from users.trustee import Trustee
from servers.CA_server import CA_server
from servers.A_server import A_server
from servers.E_server import E_server
from servers.S_server import S_server

ELGAMAL_PRIME_SIZE = 512


def update_elgamal_parameters(name):

    print('Creating El Gamal parameters for', name)

    path = f"{paths.ELGAMAL_PARAMETERS_PATH}/{name}.json"

    if not (os.path.isfile(path)):
        print('There is no file, we need to generate new parameters')
        large_prime = generate_large_safe_prime(ELGAMAL_PRIME_SIZE)
        generator = generate_generator(large_prime)
        private_key = generate_private_key()
        public_key = generate_public_key(large_prime, generator,private_key)

        parameters = {"name": name, "large_prime": large_prime,
                      "generator": generator, "private_key": private_key, "public_key": public_key}

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(parameters, f, ensure_ascii=False, indent=4)

    else:
        print('parameters already exist at', path)
        file = open(path)

        parameters = json.load(file)

        file.close()
    print()
    return parameters


def update_election_parameters():

    path = paths.ELECTION_PARAMETERS_PATH
    print('Creating El Gamal parameters for the election')
    if not (os.path.isfile(path)):
        print('There is no file, we need to generate new parameters')
        id = str(uuid.uuid1())
        large_prime = generate_large_safe_prime(ELGAMAL_PRIME_SIZE)
        generator = generate_generator(large_prime)

        election_parameters = {
            "id": id, "large_prime": large_prime, "generator": generator}

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(election_parameters, f, ensure_ascii=False, indent=4)

    else:
        print('parameters already exist at', path)
        file = open(path)

        election_parameters = json.load(file)

        file.close()
    print()
    return election_parameters


def update_trustees():

    trustees = []

    path = f"{paths.CONFIG_PATH}/trustees.json"

    print('we are loading ', path)

    file = open(path)

    data = json.load(file)

    print('trustees created :')
    for trustee in data['trustee']:

        first_name = trustee["prenom"]
        last_name = trustee["nom"]
        email = trustee["email"]

        new_trustee = Trustee(first_name, last_name, email)
        print(new_trustee)
        trustees.append(new_trustee)

    file.close()
    print()
    return trustees


def update_voters():

    voters = []

    path = f"{paths.CONFIG_PATH}/voters.json"
    print('we are loading ', path)
    file = open(path)

    data = json.load(file)
    print('voters created :')
    for voter in data['votant']:

        first_name = voter["prenom"]
        last_name = voter["nom"]
        email = voter["email"]

        new_voter = Voter(first_name, last_name, email)
        print(new_voter)
        voters.append(new_voter)

    file.close()
    print()
    return voters


def update_election_data():

    path = f"{paths.CONFIG_PATH}/election_data.json"
    print('we are loading ', path)

    file = open(path)

    election_data = json.load(file)

    file.close()
    print()
    return election_data


def election_setup():
    print("######### Election setup ###########\n")

    elgamal_parameters_CA_server = update_elgamal_parameters("CA_server")

    ca_server = CA_server(elgamal_parameters_CA_server)

    election_parameters = update_election_parameters()

    trustees = update_trustees()

    voters = update_voters()

    election_data = update_election_data()

    for voter in voters:

        voter.set_ca_server(ca_server)
    
    for trustee in trustees:

        trustee.set_ca_server(ca_server)

    elgamal_parameters_A_server = update_elgamal_parameters("A_server")

    a_server = A_server(trustees, voters, election_data, elgamal_parameters_A_server, election_parameters, ca_server)

    elgamal_parameters_E_server = update_elgamal_parameters("E_server")

    e_server = E_server(voters, elgamal_parameters_E_server, election_parameters, ca_server)

    e_server.generate_credentials_and_pub()

    for voter in voters:

        if voter.download_and_check_certificate(e_server):

            voter.download_election_parameters(e_server)

            voter.generate_blowfish_key()

            voter.cipher_and_send_blowfish_key(e_server)

            print()

    e_server.send_ciphered_credentials()

    for voter in voters:
        voter.recompute_elgamal_keys()

    print()

    print("E_server is removing the pubs, the credentials and the blowfish keys")
    e_server.remove_credentials()
    e_server.remove_blowfish_keys()
    e_server.shuffle_pubs()
    e_server.sending_pubs(a_server)

    for trustee in trustees:

        if trustee.download_and_check_certificate(a_server):

            trustee.download_election_parameters(a_server)

            trustee.generate_keys()
    print()

    a_server.ask_trustees_public_key()

    election_public_data = {"données_de_vote": election_data, "paramètres": election_parameters,
                            "trustees_keys": a_server.get_trustees_public_keys(), "codes_de_vote": a_server.get_pubs(),
                            "resultat": None}

    elgamal_parameters_S_server = update_elgamal_parameters("S_server")
    s_server = S_server(elgamal_parameters_S_server, ca_server, election_public_data)
    print("S_server is ccreated and received the election data")
    return a_server, e_server, s_server, voters, trustees



