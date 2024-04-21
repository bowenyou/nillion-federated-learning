import os

from dotenv import load_dotenv

load_dotenv()

CONFIG_PROGRAM_NAME = "nillion_federated_learning"

MODEL_PATH = "models/model_epoch_{}.pth"
DATA_PATH = "data/data_{}.pt"
PARTY_MODEL_PATH = "models/model_epoch_{}_party_{}.pth"

N_PARTIES = 2

# server config
CONFIG_SERVER = {
    "userkey_file": os.getenv("NILLION_USERKEY_PATH_SERVER"),
    "nodekey_file": os.getenv("NILLION_NODEKEY_PATH_SERVER"),
    "party_name": "server",
    "secrets": {},
}

# n parties config
CONFIG_PARTIES = [
    {
        "userkey_file": os.getenv(f"NILLION_USERKEY_PATH_PARTY_{i}"),
        "nodekey_file": os.getenv(f"NILLION_NODEKEY_PATH_PARTY_{i}"),
        "party_name": f"Party{i}",
    }
    for i in range(N_PARTIES)
]
