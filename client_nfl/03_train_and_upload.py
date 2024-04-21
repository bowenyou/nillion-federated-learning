import argparse
import asyncio
import json
import os
import sys

import py_nillion_client as nillion
import pytest
import torch
from config import (
    CONFIG_PARTIES,
    CONFIG_PROGRAM_NAME,
    CONFIG_SERVER,
    DATA_PATH,
    MODEL_PATH,
    N_PARTIES,
    PARTY_MODEL_PATH,
)
from dotenv import load_dotenv
from model import Model, dequantize_model, secretize_model
from torch.utils.data import DataLoader

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from helpers.nillion_client_helper import create_nillion_client
from helpers.nillion_keypath_helper import getNodeKeyFromFile, getUserKeyFromFile

load_dotenv()


def load_model(epoch):

    model = Model()
    model.load_state_dict(torch.load(MODEL_PATH.format(epoch)))
    dequantize_model(model)

    return model


def load_dataset(party_id):

    X, y = torch.load(DATA_PATH.format(party_id))

    return X, y


def train_one_epoch(party_id, epoch):

    model = load_model(epoch)
    for param in model.state_dict():
        print(param, model.state_dict()[param])
    X, y = load_dataset(party_id)

    dataset = torch.utils.data.TensorDataset(X, y)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = torch.nn.CrossEntropyLoss()

    model.train()

    for data, target in dataloader:

        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)

        loss.backward()
        optimizer.step()

    print(f"Epoch: {epoch}, Party: {party_id}, Batch loss: {loss.item():.4f}")

    secret, _ = secretize_model(model, party_id)
    torch.save(model.state_dict(), PARTY_MODEL_PATH.format(epoch, party_id))

    return secret


async def main(args=None):

    parser = argparse.ArgumentParser(description="Train and store a localized model")

    parser.add_argument(
        "--epoch",
        required=True,
        type=int,
        help="the epoch of the training process",
    )

    args = parser.parse_args(args)
    epoch = args.epoch

    cluster_id = os.getenv("NILLION_CLUSTER_ID")

    client = create_nillion_client(
        getUserKeyFromFile(CONFIG_SERVER["userkey_file"]),
        getNodeKeyFromFile(CONFIG_SERVER["nodekey_file"]),
    )
    user_id = client.user_id()

    party_clients = [
        create_nillion_client(
            getUserKeyFromFile(CONFIG_PARTIES[i]["userkey_file"]),
            getNodeKeyFromFile(CONFIG_PARTIES[i]["nodekey_file"]),
        )
        for i in range(N_PARTIES)
    ]

    program_id = f"{user_id}/{CONFIG_PROGRAM_NAME}"

    if epoch == 0:
        store_ids = {}
    else:
        with open("data/store_ids.json", "r") as f:
            store_ids = json.load(f)

    for i in range(N_PARTIES):
        secret = train_one_epoch(i, epoch)
        # Create input bindings for the program
        secret_bindings = nillion.ProgramBindings(program_id)
        secret_bindings.add_input_party(f"Party{i}", party_clients[i].party_id())

        # Create permissions object
        permissions = nillion.Permissions.default_for_user(party_clients[i].user_id())

        # Give compute permissions to the first party
        compute_permissions = {
            client.user_id(): {program_id},
        }
        permissions.add_compute_permissions(compute_permissions)

        # Store the permissioned secret
        if epoch == 0:
            store_id = await party_clients[i].store_secrets(
                cluster_id, secret_bindings, secret, permissions
            )
            print(f"Party {i} store id: {store_id}")
            store_ids[i] = store_id

        else:
            await party_clients[i].update_secrets(
                cluster_id, store_ids[str(i)], None, secret
            )

    if epoch == 0:
        with open("data/store_ids.json", "w") as f:
            json.dump(store_ids, f, indent=4)


if __name__ == "__main__":
    asyncio.run(main())


@pytest.mark.asyncio
async def test_main():
    pass
