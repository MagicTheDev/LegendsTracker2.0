from __future__ import annotations
from dotenv import load_dotenv
load_dotenv()

import coc
import os

coc_client = coc.Client(key_names="test")
COC_EMAIL = os.getenv("BETA_COC_EMAIL")
COC_PASSWORD = os.getenv("BETA_COC_PASSWORD")

async def setup_coc():
    try:
        await coc_client.login(email=COC_EMAIL, password=COC_PASSWORD)
    except Exception as Exc:
        print(f"Failed to setup clash api connection {Exc}")
        exit(1)