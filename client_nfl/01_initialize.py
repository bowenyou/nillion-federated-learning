import asyncio
import os
import sys

import pytest
import torch
from config import DATA_PATH, MODEL_PATH, N_PARTIES
from dotenv import load_dotenv
from model import Model, quantize_model, secretize_model
from program_template import fill_in_template
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()


def split_data_for_parties(X, y, n_parties=N_PARTIES):

    dataset = torch.utils.data.TensorDataset(X, y)
    dataset = shuffle(dataset, random_state=42)

    total_data_size = len(dataset)
    data_per_party = total_data_size // n_parties

    for i in range(n_parties):
        start_index = i * data_per_party
        end_index = min((i + 1) * data_per_party, total_data_size)

        split_data = dataset[start_index:end_index]
        X_party = torch.stack([item[0] for item in split_data])
        y_party = torch.tensor([item[1] for item in split_data])

        torch.save((X_party, y_party), DATA_PATH.format(i))


async def main():
    # initialize the global model state
    model = Model()
    quantize_model(model)

    torch.save(model.state_dict(), MODEL_PATH.format(0))

    _, secret_keys = secretize_model(model, 0)

    # generate nada program
    with open("../programs/nillion_federated_learning.py", "w") as f:
        f.write(fill_in_template(secret_keys, N_PARTIES))

    # split global dataset among parties
    (X, y) = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    X = torch.tensor(X_train, dtype=torch.float32)
    y = torch.tensor(y_train, dtype=torch.long)

    split_data_for_parties(X, y)

    X_test = torch.tensor(X_test, dtype=torch.float32)
    y_test = torch.tensor(y_test, dtype=torch.long)

    torch.save((X_test, y_test), "data/test_data.pt")


if __name__ == "__main__":
    asyncio.run(main())


@pytest.mark.asyncio
async def test_main():
    pass
