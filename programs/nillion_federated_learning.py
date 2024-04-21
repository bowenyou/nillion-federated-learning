from nada_dsl import *

KEYS = [
    "fc1.weight_0_0_party{}",
    "fc1.weight_0_1_party{}",
    "fc1.weight_0_2_party{}",
    "fc1.weight_0_3_party{}",
    "fc1.weight_1_0_party{}",
    "fc1.weight_1_1_party{}",
    "fc1.weight_1_2_party{}",
    "fc1.weight_1_3_party{}",
    "fc1.weight_2_0_party{}",
    "fc1.weight_2_1_party{}",
    "fc1.weight_2_2_party{}",
    "fc1.weight_2_3_party{}",
    "fc1.weight_3_0_party{}",
    "fc1.weight_3_1_party{}",
    "fc1.weight_3_2_party{}",
    "fc1.weight_3_3_party{}",
    "fc1.weight_4_0_party{}",
    "fc1.weight_4_1_party{}",
    "fc1.weight_4_2_party{}",
    "fc1.weight_4_3_party{}",
    "fc1.weight_5_0_party{}",
    "fc1.weight_5_1_party{}",
    "fc1.weight_5_2_party{}",
    "fc1.weight_5_3_party{}",
    "fc1.weight_6_0_party{}",
    "fc1.weight_6_1_party{}",
    "fc1.weight_6_2_party{}",
    "fc1.weight_6_3_party{}",
    "fc1.weight_7_0_party{}",
    "fc1.weight_7_1_party{}",
    "fc1.weight_7_2_party{}",
    "fc1.weight_7_3_party{}",
    "fc1.bias_0_party{}",
    "fc1.bias_1_party{}",
    "fc1.bias_2_party{}",
    "fc1.bias_3_party{}",
    "fc1.bias_4_party{}",
    "fc1.bias_5_party{}",
    "fc1.bias_6_party{}",
    "fc1.bias_7_party{}",
    "fc2.weight_0_0_party{}",
    "fc2.weight_0_1_party{}",
    "fc2.weight_0_2_party{}",
    "fc2.weight_0_3_party{}",
    "fc2.weight_0_4_party{}",
    "fc2.weight_0_5_party{}",
    "fc2.weight_0_6_party{}",
    "fc2.weight_0_7_party{}",
    "fc2.weight_1_0_party{}",
    "fc2.weight_1_1_party{}",
    "fc2.weight_1_2_party{}",
    "fc2.weight_1_3_party{}",
    "fc2.weight_1_4_party{}",
    "fc2.weight_1_5_party{}",
    "fc2.weight_1_6_party{}",
    "fc2.weight_1_7_party{}",
    "fc2.weight_2_0_party{}",
    "fc2.weight_2_1_party{}",
    "fc2.weight_2_2_party{}",
    "fc2.weight_2_3_party{}",
    "fc2.weight_2_4_party{}",
    "fc2.weight_2_5_party{}",
    "fc2.weight_2_6_party{}",
    "fc2.weight_2_7_party{}",
    "fc2.bias_0_party{}",
    "fc2.bias_1_party{}",
    "fc2.bias_2_party{}",
]

N_PARTIES = 2

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