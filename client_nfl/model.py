import numpy as np
import py_nillion_client as nillion
import torch
import torch.nn as nn
import torch.nn.functional as F


# helper function to quantize weights to integer values
def quantize(num):

    whole_num = int(num)
    fractional_part = int((num - whole_num) * 65536)
    fp_number = (whole_num << 16) + fractional_part

    if fp_number == 0:
        return 65537

    return fp_number


def dequantize(num):

    if num == 65537:
        return 0.0

    whole_num = int(num) >> 16
    fractional_part = (int(num) & 0xFFFF) / 65536.0
    return whole_num + fractional_part


def quantize_model(model):
    for param in model.parameters():
        param.data = torch.tensor(
            np.array([quantize(x) for x in param.data.flatten()]), dtype=torch.float32
        ).reshape(param.data.shape)


def dequantize_model(model):
    for param in model.parameters():
        param.data = torch.tensor(
            np.array([dequantize(x) for x in param.data.flatten()]), dtype=torch.float32
        ).reshape(param.data.shape)


def secretize_model(model, party_id):

    quantize_model(model)
    secrets = {}
    secret_keys = []
    for layer_name, tensor in model.state_dict().items():
        if tensor.ndim == 2:
            for i in range(tensor.size(0)):
                for j in range(tensor.size(1)):
                    secrets[f"{layer_name}_{i}_{j}_party{party_id}"] = (
                        nillion.SecretInteger(int(tensor[i, j].item()))
                    )

                    secret_keys.append(f"{layer_name}_{i}_{j}_party{{}}")
        if tensor.ndim == 1:
            for i in range(tensor.size(0)):
                secrets[f"{layer_name}_{i}_party{party_id}"] = nillion.SecretInteger(
                    int(tensor[i].item())
                )

                secret_keys.append(f"{layer_name}_{i}_party{{}}")

    return nillion.Secrets(secrets), secret_keys


def desecretize_model(result):

    model = Model()
    state_dict = model.state_dict()

    for k, v in result.items():
        temp = k.split("_")
        param_index = temp[0]

        if "bias" in param_index:
            state_dict[param_index][int(temp[1])] = v
        else:
            state_dict[param_index][int(temp[1]), int(temp[2])] = v

    model.load_state_dict(state_dict)

    return model


class Model(nn.Module):

    def __init__(self):

        super().__init__()

        self.relu = nn.ReLU()
        self.fc1 = nn.Linear(4, 8)
        self.fc2 = nn.Linear(8, 3)

    def forward(self, x):

        x = self.relu(self.fc1(x))
        x = F.softmax(self.fc2(x))

        return x
