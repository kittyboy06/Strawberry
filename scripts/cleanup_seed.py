"""Remove all subjects, experiments, versions, and storage objects from Supabase."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import httpx

workspace_root = Path(__file__).resolve().parents[1]
load_dotenv(workspace_root / ".env")

raw_url = os.getenv("STRAWBERRY_SUPABASE_URL", "").strip().rstrip("/")
if raw_url.endswith("/rest/v1"):
    raw_url = raw_url[:-len("/rest/v1")].rstrip("/")

SUPABASE_URL = raw_url
SECRET_KEY = os.getenv("STRAWBERRY_SUPABASE_SECRET_KEY", "")

if not SUPABASE_URL or not SECRET_KEY:
    print("Error: Missing STRAWBERRY_SUPABASE_URL or STRAWBERRY_SUPABASE_SECRET_KEY in .env")
    sys.exit(1)

headers = {
    "apikey": SECRET_KEY,
    "Authorization": f"Bearer {SECRET_KEY}",
    "Content-Type": "application/json",
}


def list_storage_objects(client: httpx.Client, prefix: str = "") -> list[str]:
    res = client.post(
        f"{SUPABASE_URL}/storage/v1/object/list/programs",
        headers=headers,
        json={"prefix": prefix, "limit": 1000},
    )
    if res.status_code != 200:
        return []
    paths: list[str] = []
    for item in res.json():
        full = f"{prefix}/{item['name']}" if prefix else item["name"]
        if item.get("id") is None:
            paths.extend(list_storage_objects(client, full))
        else:
            paths.append(full)
    return paths


print(f"Cleaning subjects & 'programs' storage bucket on: {SUPABASE_URL}")

with httpx.Client(timeout=15.0) as client:
    objects = list_storage_objects(client)
    print(f"Found {len(objects)} storage objects in 'programs' bucket.")
    if objects:
        for idx in range(0, len(objects), 100):
            batch = objects[idx : idx + 100]
            client.request(
                "DELETE",
                f"{SUPABASE_URL}/storage/v1/object/programs",
                headers=headers,
                json={"prefixes": batch},
            )

    for table in ("experiment_versions", "experiments", "subjects"):
        r = client.delete(f"{SUPABASE_URL}/rest/v1/{table}?id=not.is.null", headers=headers)
        print(f"Cleared {table}: HTTP {r.status_code}")
