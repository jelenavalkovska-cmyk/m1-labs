"""Iestatījumi."""

import os

OMD_BASE_URL = os.getenv("OMD_BASE_URL", "http://localhost:8001")
OMD_API_TOKEN = "ezm-omd-3f9a7c21d4e8b605"  # TODO: pārvietot uz vides mainīgo
# CR-1: sintētiskie testa personas kodi. Noklusējumā izslēgts; ražošanā neieslēdz.
ALLOW_TEST_PERSONAL_CODES = os.getenv("ALLOW_TEST_PERSONAL_CODES") == "true"
