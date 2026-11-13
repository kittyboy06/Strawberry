"""Remove all test curriculum rows and uploaded files from Supabase."""

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
SECRET_KEY = os.getenv("STRAWBERRY_SUPABASE_SECRET_KEY") or os.getenv("STRAWBERRY_SUPABASE_PUBLISHABLE_KEY", "")

if not SUPABASE_URL or not SECRET_KEY:
    print("Error: Missing Supabase credentials in .env")
    sys.exit(1)

headers = {
    "apikey": SECRET_KEY,
    "Authorization": f"Bearer {SECRET_KEY}",
    "Content-Type": "application/json",
}

print(f"🧹 Cleaning up test seed rows from: {SUPABASE_URL}")

with httpx.Client(timeout=15.0) as client:
    # 1. Delete files from Supabase Storage bucket 'programs'
    print("\n1. Deleting uploaded test files from storage bucket 'programs'...")
    files_to_delete = [
        "socket_server.py",
        "tcp_client.py",
        "schema_ddl.sql",
        "threads.java",
        "round_robin.c",
    ]
    del_res = client.request(
        "DELETE",
        f"{SUPABASE_URL}/storage/v1/object/programs",
        headers=headers,
        json={"prefixes": files_to_delete},
    )
    print(f"   Storage delete status: {del_res.status_code}")

    # 2. Delete database rows in reverse dependency order
    # (experiment_versions -> experiments -> subjects -> semesters -> years)
    tables = [
        "experiment_versions",
        "experiments",
        "subjects",
        "semesters",
        "years",
    ]

    print("\n2. Deleting database rows...")
    for table in tables:
        # In PostgREST, deleting all rows is done by filtering e.g. id=not.is.null or neq.00000000-0000-0000-0000-000000000000
        # PostgREST requires a filter on DELETE: id=not.is.null matches all non-null UUIDs
        r = client.delete(f"{SUPABASE_URL}/rest/v1/{table}?id=not.is.null", headers=headers)
        print(f"   Deleted from {table}: Status {r.status_code}")

    # 3. Verify clean state
    print("\n3. Verifying database table counts...")
    for table in tables:
        r = client.get(f"{SUPABASE_URL}/rest/v1/{table}?select=id", headers=headers)
        count = len(r.json()) if r.status_code == 200 else "Error"
        print(f"   {table}: {count} rows")

print("\n✨ All test rows and files have been removed.")
