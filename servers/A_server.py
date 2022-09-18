from .Server import Server
import uuid


class A_server(Server):

    def __init__(self, trustees, voters, election_data, elgamal_parameters, election_parameters, ca_server):
        super().__init__(elgamal_parameters, election_parameters, ca_server)

        self._election_data = election_data
        self._trustees = trustees
        self._voters = voters
        self.set_voters_uuid()
        self._trustees_public_keys = []

    def set_voters_uuid(self):

        for voter in self._voters :
            u_id = uuid.uuid1().int
            voter.set_uuid(u_id)

    def set_pubs(self, pubs):

        self._pubs = pubs
    
    def ask_trustees_public_key(self):
        print("A_server is asking trustees public keys")
        for trustee in self._trustees:
            
            trustee_public_key = trustee.get_public_key()
            self._trustees_public_keys.append(trustee_public_key)
        print()
    
    def get_trustees_public_keys(self):

        return self._trustees_public_keys

    def get_pubs(self):

        return self._pubs
    