
def make_one_voter_vote(voters, S_server):
    i = 1
    for voter in voters:

        print(i, " > ", voter.get_first_name())
        i += 1

    voter = input("Which voter do you want to make vote : ")

    allowed_choices = [str(x + 1) for x in range(len(voters))]

    while voter not in allowed_choices:
        print("please choose a valid answer")
        voter = input("Which voter do you want to make vote : ")
    voters[int(voter)-1].vote(S_server)

def make_one_trustee_audit(trustees, S_server, a_server):
    i = 1
    for trustee in trustees:

        print(i, " > ", trustee.get_first_name())
        i += 1

    trustee = input("Which trustee do you want to make vote : ")
    allowed_choices = [str(x + 1) for x in range(len(trustees))]

    while trustee not in allowed_choices:
        print("please choose a valid answer")
        trustee = input("Which trustee do you want to make vote : ")

    return trustees[int(trustee)-1].audit(S_server, a_server)

def make_one_voter_check_vote(voters, S_server):

    S_server.show_registered_ballots_hashed()
    i = 1
    for voter in voters:
        print(i, " > ", voter.get_first_name())
        i += 1

    voter = input("Which voter should check his vote : ")

    allowed_choices = [str(x + 1) for x in range(len(voters))]

    while voter not in allowed_choices:
        print("please choose a valid answer")
        voter = input("Which voter should check his vote : ")

    voter_ballot_hash = voters[int(voter) - 1].get_ballot_hash()

    print("the hash of the ballot sent is : ", voter_ballot_hash)

    if voter_ballot_hash in S_server.get_ballots_hash():

        print("OK : The vote has been received")

        return True

    else :

        print("FALSE : The vote has not been received")

        return False
