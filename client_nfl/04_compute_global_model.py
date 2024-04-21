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
from model import Model, desecretize_model, secretize_model
from torch.utils.data import DataLoader

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from helpers.nillion_client_helper import create_nillion_client
from helpers.nillion_keypath_helper import getNodeKeyFromFile, getUserKeyFromFile

load_dotenv()


# The server stores the program
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
    party_id = client.party_id()

    program_id = f"{user_id}/{CONFIG_PROGRAM_NAME}"

    with open("data/store_ids.json", "r") as f:
        store_ids = json.load(f)

    party_clients = [
        create_nillion_client(
            getUserKeyFromFile(CONFIG_PARTIES[i]["userkey_file"]),
            getNodeKeyFromFile(CONFIG_PARTIES[i]["nodekey_file"]),
        )
        for i in range(N_PARTIES)
    ]

    compute_bindings = nillion.ProgramBindings(program_id)
    compute_bindings.add_output_party(CONFIG_SERVER["party_name"], party_id)

    for i in range(N_PARTIES):
        compute_bindings.add_input_party(
            CONFIG_PARTIES[i]["party_name"], party_clients[i].party_id()
        )

    print(f"Computing using program {program_id}")

    # Compute on the secret with all store ids. Note that there are no compute time secrets or public variables
    compute_id = await client.compute(
        cluster_id,
        compute_bindings,
        list(store_ids.values()),
        nillion.Secrets({}),
        nillion.PublicVariables({}),
    )

    result = None

    # Print compute result
    print(f"The computation was sent to the network. compute_id: {compute_id}")
    while True:
        compute_event = await client.next_compute_event()
        if isinstance(compute_event, nillion.ComputeFinishedEvent):
            print(f"Compute complete for compute_id {compute_event.uuid}")
            result = compute_event.result.value
            break

    # desecretize model
    model = desecretize_model(result)
    # store model after dequantizing it
    torch.save(model.state_dict(), MODEL_PATH.format(epoch + 1))

    for params in model.state_dict():
        print(params, model.state_dict()[params])


if __name__ == "__main__":
    asyncio.run(main())


@pytest.mark.asyncio
async def test_main():
    pass
