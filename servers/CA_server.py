from crypto.certificates import generate_self_signed_certificate, generate_certificate
import paths

import os
import json


class CA_server:

    def __init__(self, elgamal_parameters):

        self._name = elgamal_parameters["name"]
        print("creation of server", self._name)
        self._large_prime = elgamal_parameters["large_prime"]
        self._generator = elgamal_parameters["generator"]
        self._private_key = elgamal_parameters["private_key"]
        self._public_key = elgamal_parameters["public_key"]
        self.set_certificate()
        print()

    def set_certificate(self):
        
        cert_path = f"{paths.CERTIFICATES_PATH}/{self._name}.json"
        print("creation of a self-signed certficate for ", self._name)
        if not (os.path.isfile(cert_path)):

            self._certificate = generate_self_signed_certificate(
                self._name,
                self._large_prime,
                self._generator,
                self._public_key,
                self._private_key)

            with open(cert_path, 'w', encoding='utf-8') as f:
                json.dump(self._certificate, f, ensure_ascii=False, indent=4)

        else:

            file = open(cert_path)

            self._certificate = json.load(file)

            file.close()

    def get_public_key(self):

        return self._public_key

    def get_certificate(self):

        return self._certificate

    def creating_a_certificate(self, name, large_prime, generator, public_key):

        certificate = generate_certificate(
            name,
            large_prime,
            generator,
            public_key,
            self._private_key,
            self._certificate)

        return certificate

