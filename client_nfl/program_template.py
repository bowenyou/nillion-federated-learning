TEMPLATE = """
from nada_dsl import *

KEYS = [
    ### WEIGHTS ###
]

N_PARTIES = ### PARTIES ###

def nada_main():
    
    server = Party(name="server")
    parties = []
    for i in range(N_PARTIES):
        parties.append(Party(name=f"Party{i}"))

    output = []
    for k in KEYS:

        temp = SecretInteger(Input(name=k.format(0), party=parties[0]))
        for i in range(1, N_PARTIES):
            temp += SecretInteger(Input(name=k.format(i), party=parties[i]))

        temp = temp / Integer(N_PARTIES)

        output.append(Output(temp, k, server))

    return output
"""


def fill_in_template(keys, n_parties):

    keys_section = "\n".join([f"""    "{k}",""" for k in keys])

    filled_template = TEMPLATE.replace("    ### WEIGHTS ###", keys_section).replace(
        "### PARTIES ###" "", str(n_parties)
    )

    return filled_template.strip()
