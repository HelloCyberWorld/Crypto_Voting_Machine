import os
dir = os.path.dirname(os.path.realpath('__file__'))
ELECTION_PARAMETERS_PATH = dir + "/preload/election_parameters.json"
ELGAMAL_PARAMETERS_PATH = dir + "/preload/elgamal_parameters"
CERTIFICATES_PATH = dir + "/preload/certificates"
ELGAMAL_PRIME_SIZE = 512
CONFIG_PATH = dir + "/config"

