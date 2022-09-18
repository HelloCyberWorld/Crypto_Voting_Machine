import json
from crypto.elgamal import check_knowledge, check_signature, decrypt_list_of_vectors
from crypto.utils import fast_exponentiation, modular_inverse
from crypto.sha1 import sha1, to_hex
from .Server import Server
import collections


def value_inferior_exist_in_list( list, value):

    if value <= 1 :

        return True

    if list.count(value-1) >= 1:
        return True
    else:

        return False


class S_server(Server):

    def __init__(self, elgamal_parameters, ca_server, election_public_data):
        election_parameters = election_public_data["paramètres"]
        super().__init__(elgamal_parameters, election_parameters, ca_server)
        self._voting_data = election_public_data["données_de_vote"]
        self._election_parameters = election_public_data["paramètres"]
        self._trustees_public_keys = election_public_data["trustees_keys"]
        self._pubs = election_public_data["codes_de_vote"]
        self._result = election_public_data["resultat"]
        self.compute_global_key()
        self._hashed_ballots = []
        self._ballots = []
        self._global_private_key = 0

    def show_registered_ballots_hashed(self):

        print("registered ballots are : ")

        for ballot in self._hashed_ballots:
            print(ballot)

    def get_ballots(self):

        return self._ballots

    def get_ballots_hash(self):

        return self._hashed_ballots

    def check_and_add_ballot(self, ballot):

        print(self._name, " has receive a ballot from a voter")

        generator = self._election_parameters["generator"]
        large_prime = self._election_parameters["large_prime"]
        voter_public_key = ballot["voter_public_key"]

        vector = ballot["ciphered_choices"]
        proof = ballot["proof"]
        signature = proof["signature"]

        is_in_list = (voter_public_key in self._pubs)
        vector_string = json.dumps(vector)
        good_signature = check_signature(vector_string, signature, large_prime, generator, voter_public_key)
        knows_private_key = check_knowledge(large_prime, generator, vector, proof, voter_public_key)
        has_already_voted = False

        print(self._name, " is checking the ballot")

        for ball in self._ballots:

            if ball["voter_public_key"] == voter_public_key:

                has_already_voted = True
                print("this voter has already voted, you can't vote twice")

                return False

        if is_in_list and knows_private_key and good_signature:

            ballot_string = json.dumps(ballot)
            ballot_bytes = bytes(ballot_string, 'utf8')
            self._ballots.append(ballot)
            hashed_ballot = sha1(ballot_bytes)
            hashed_ballot = to_hex(hashed_ballot)

            self._hashed_ballots.append(hashed_ballot)
            print(self._name, ": the ballot is OK")
            return True

        else:
            print(self._name, ": the ballot is WRONG")
            return False

    def add_trustee_private_key(self, ciphered, shared_secret):

        large_prime = self._election_parameters["large_prime"]

        s = fast_exponentiation(shared_secret, self._private_key, self._large_prime)
        plain_key = (ciphered * modular_inverse(s, self._large_prime)) % self._large_prime

        self._global_private_key = (self._global_private_key + plain_key) % large_prime

    def get_voting_data(self):

        return self._voting_data

    def get_election_parameters(self):

        return self._election_parameters

    def get_trustees_public_key(self):

        return self._trustees_public_keys

    def get_global_key(self):

        return self._global_key

    def compute_global_key(self):

        tmp = 1

        for key in self._trustees_public_keys:
            tmp = (tmp * key)

        self._global_key = tmp % self._election_parameters["large_prime"]

    def decipher_ballots(self):

        deciphered_list_of_vectors = []
        ballots = self._ballots
        large_prime = self._election_parameters["large_prime"]
        generator = self._election_parameters["generator"]

        for ballot in ballots:
            ciphered = ballot["ciphered_choices"]

            plain_vector = decrypt_list_of_vectors(ciphered, generator, large_prime, self._global_private_key)

            deciphered_list_of_vectors.append(plain_vector)

        return deciphered_list_of_vectors

    def counting(self):

        all_voters_answers_to_each_question = []

        deciphered_list_of_vectors = self.decipher_ballots()

        print("deciphered list of vectors for all voters : ", deciphered_list_of_vectors)

        new_deciphered_list_of_vectors = []  # ex : vector [0, 1, 0] = > 2

        for j in range(len(deciphered_list_of_vectors)):
            tmp = []
            for i in range(len(deciphered_list_of_vectors[j])):

                tmp.append( deciphered_list_of_vectors[j][i].index(1) + 1 )

            new_deciphered_list_of_vectors.append(tmp)

        print("list of vectors transformed to list of int: ", new_deciphered_list_of_vectors)

        for j in range(len(new_deciphered_list_of_vectors[0])):
            tmp = []
            for i in range(len(new_deciphered_list_of_vectors)):

                tmp.append(new_deciphered_list_of_vectors[i][j])

            all_voters_answers_to_each_question.append(tmp)

        print("answers grouped by question : ", all_voters_answers_to_each_question)

        most_common_answer_list = []

        for question in all_voters_answers_to_each_question:

            counter = collections.Counter(question)

            most_common = counter.most_common(len(question))

            print("most_common", most_common)

            if len(most_common) == len(question) and len(question) > 1:

                most_common_answer_list.append(0)

            else:

                most_common_answer_list.append(most_common[0][0])

        print("most common answer for each question : ", most_common_answer_list)

        return most_common_answer_list

    def counting_ordered(self):

        list_of_vectors = self.decipher_ballots()

        sorted_by_question = []

        sorted_by_question_candidate = []

        points_list = []

        all_voters_answers_to_each_question = []

        print("deciphered list of vectors for all voters : ", list_of_vectors)

        for j in range(len(list_of_vectors[0])):

            question = []

            for i in range(len(list_of_vectors)):
                question.append(list_of_vectors[i][j])

            sorted_by_question.append(question)

        print("sorted by question : ", sorted_by_question)

        for question in sorted_by_question:

            tmp = []

            for k in range(len(question[0])):
                candidate = []

                for l in range(len(question)):
                    candidate.append(question[l][k])

                tmp.append(candidate)

            sorted_by_question_candidate.append(tmp)

        print("sorted by question and candidate : ", sorted_by_question_candidate)

        question_candidate_points_list = []

        for question in sorted_by_question_candidate:

            candidate_points_list = []

            for candidate in question:
                points = sum(candidate)
                candidate_points_list.append(points)

            question_candidate_points_list.append(candidate_points_list)

        print("transformed order to points : ", question_candidate_points_list)

        order_list = []

        for question in question_candidate_points_list:

            max_value = max(question) + 1  # on remplace les élément par cette valeur pour distinguer ce qui a été traité ou non
            tmp = []
            while question != ( [max_value] * len(question) ):

                min_value = min(question) # min = 6

                index = question.index(min_value)

                while question.count(min_value) > 0:

                    index_tmp = question.index(min_value)

                    tmp.append(index + 1)

                    question[index_tmp] = max_value


            order_list.append(tmp)

        print("candidate order per question : ", order_list)

        return order_list



    def claim_winner_ordered(self):

        win_list = self.counting_ordered()

        questions = self._voting_data["questions"]

        for i in range(len(questions)):

            candidates = questions[i]["reponses"]

            for j in range(len(candidates)):

                list = win_list[i]

                value = win_list[i][j]

                x = value

                while value_inferior_exist_in_list(list, x) == False:

                    x-=1
                    value = x

                print(candidates[j], " is at position ", value)



    def claim_winner(self):

        win_list = self.counting()
        questions = self._voting_data["questions"]

        for i in range(len(questions)):

            rep = questions[i]["reponses"]

            win_index = win_list[i]

            if win_list[i] == 0:

                print(questions[i]["question"], " : It's a tie...")

            else:

                print(questions[i]["question"]," : the winner is ", rep[win_index - 1])



    def get_result(self):

        if len(self._ballots) > 0:

            if self._voting_data["type"] == 1:
                self.claim_winner()

            else :

                self.claim_winner_ordered()
        else:
            print("No registered ballots")










