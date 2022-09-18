import json
import paths


class Server:

    def __init__(self, elgamal_parameters,election_parameters, ca_server):

        self._name = elgamal_parameters["name"]
        print("creation of server", self._name)
        self._large_prime = elgamal_parameters["large_prime"]
        self._generator = elgamal_parameters["generator"]
        self._private_key = elgamal_parameters["private_key"]
        self._public_key = elgamal_parameters["public_key"]
        self._ca_server = ca_server
        self.set_certificate()
        self._election_parameters = election_parameters
        print()


    def get_election_parameters(self):

        return self._election_parameters

    def set_certificate(self):
        print("creation of a certficate for ", self._name, "signed by CA_server")
        self._certificate = self._ca_server.creating_a_certificate(
            self._name,
            self._large_prime,
            self._generator,
            self._public_key)

        cert_path = f"{paths.CERTIFICATES_PATH}/{self._name}.json"

        with open(cert_path, 'w', encoding='utf-8') as f:

            json.dump(self._certificate, f, ensure_ascii=False, indent=4)

    def get_certificate(self):

        return self._certificate
