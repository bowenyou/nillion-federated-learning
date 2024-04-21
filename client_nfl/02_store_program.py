import asyncio
import os
import sys

import pytest
from config import CONFIG_PROGRAM_NAME, CONFIG_SERVER
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from helpers.nillion_client_helper import create_nillion_client
from helpers.nillion_keypath_helper import getNodeKeyFromFile, getUserKeyFromFile

load_dotenv()


# The server stores the program
async def main():
    cluster_id = os.getenv("NILLION_CLUSTER_ID")
    client = create_nillion_client(
        getUserKeyFromFile(CONFIG_SERVER["userkey_file"]),
        getNodeKeyFromFile(CONFIG_SERVER["nodekey_file"]),
    )
    user_id = client.user_id()

    # store program
    program_mir_path = f"../programs-compiled/{CONFIG_PROGRAM_NAME}.nada.bin"

    action_id = await client.store_program(
        cluster_id, CONFIG_PROGRAM_NAME, program_mir_path
    )

    program_id = f"{user_id}/{CONFIG_PROGRAM_NAME}"
    print("Stored program. action_id:", action_id)
    print("Stored program_id:", program_id)


if __name__ == "__main__":
    asyncio.run(main())


@pytest.mark.asyncio
async def test_main():
    pass
