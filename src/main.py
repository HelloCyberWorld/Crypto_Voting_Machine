from election_setup import election_setup
from election_utils import *

"""Déroulé de l'élection : """

menu = {}
menu['1'] = "Create an election."
menu['2'] = "Make a vote"
menu['3'] = "Check a vote"
menu['4'] = "Audit"
menu['5'] = "Counting"
menu['6'] = "Quitter"

election_launched = False

while True:

  options = menu.keys()
  sorted(options)
  print("\n","Hello master Rémi ! How can I help your majesty?")

  for entry in options:

      print(entry, " > ", menu[entry])

  selection = input("Make your choice : ")

  if selection =='1':
    """lecture des fichiers dans config et preload"""
    a_server, e_server, s_server, voters, trustees = election_setup()
    election_launched = True

  elif selection == '2':
    """Création du votes pour le votant de votre choix"""
    if election_launched:
      make_one_voter_vote(voters, s_server)

    else:
      print("No election launched")

  elif selection == '3':
    """Un votant vérifie que son vote est bien dans la liste des ballots enregistrés"""
    if election_launched:
      make_one_voter_check_vote(voters, s_server)

    else:
      print("No election launched")

  elif selection == '4':
    """Audit des trustees"""
    if election_launched:
      make_one_trustee_audit(trustees,s_server,a_server)

    else:
      print("No election launched")


  elif selection == '5':
    """Dépouillement et résultat"""

    if election_launched:

        if make_one_trustee_audit(trustees, s_server, a_server) == True :

            for trustee in trustees:
                trustee.cipher_and_send_private_key(s_server)
            s_server.get_result()

        else :
            print("The Audit is not OK, we can't announce the winner")


    else:
      print("No election launched")


  elif selection == '6':
    break

  else:
     print("Unknown Option Selected!")