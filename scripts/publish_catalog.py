"""Publish and seed laboratory curriculum data and source files to Supabase."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import httpx

# Load workspace root .env
workspace_root = Path(__file__).resolve().parents[1]
load_dotenv(workspace_root / ".env")

# Ensure strawberry_cli can be imported
sys.path.insert(0, str(workspace_root / "strawberry-cli" / "src"))
from strawberry_cli.repository.mock_data import (
    SEED_YEARS,
    SEED_SEMESTERS,
    SEED_SUBJECTS,
    SEED_EXPERIMENTS,
    DEMO_PROGRAMS,
    get_demo_hash,
)

raw_url = os.getenv("STRAWBERRY_SUPABASE_URL", "").strip().rstrip("/")
if raw_url.endswith("/rest/v1"):
    raw_url = raw_url[:-len("/rest/v1")].rstrip("/")

SUPABASE_URL = raw_url
SECRET_KEY = os.getenv("STRAWBERRY_SUPABASE_SECRET_KEY") or os.getenv("STRAWBERRY_SUPABASE_PUBLISHABLE_KEY", "")

if not SUPABASE_URL or not SECRET_KEY:
    print("Error: STRAWBERRY_SUPABASE_URL or STRAWBERRY_SUPABASE_SECRET_KEY not set in .env")
    sys.exit(1)

headers = {
    "apikey": SECRET_KEY,
    "Authorization": f"Bearer {SECRET_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates",
}

print(f"🍓 Publishing curriculum to: {SUPABASE_URL}")

with httpx.Client(timeout=15.0) as client:
    # 1. Seed Years
    print("\n1. Seeding Academic Years...")
    years_payload = [
        {"year_number": y["year_number"], "display_name": y["display_name"]}
        for y in SEED_YEARS
    ]
    r = client.post(f"{SUPABASE_URL}/rest/v1/years", headers=headers, json=years_payload)
    print(f"   Years: Status {r.status_code}")

    # Fetch inserted years to get auto-generated UUIDs
    years_data = client.get(f"{SUPABASE_URL}/rest/v1/years?select=*", headers=headers).json()
    year_map = {y["year_number"]: y["id"] for y in years_data}

    # 2. Seed Semesters
    print("2. Seeding Semesters...")
    semesters_payload = [
        {
            "year_id": year_map[s["semester_number"] // 2 if s["semester_number"] % 2 == 0 else (s["semester_number"] + 1) // 2],
            "semester_number": s["semester_number"],
            "display_name": s["display_name"],
        }
        for s in SEED_SEMESTERS
        if (s["semester_number"] // 2 if s["semester_number"] % 2 == 0 else (s["semester_number"] + 1) // 2) in year_map
    ]
    r = client.post(f"{SUPABASE_URL}/rest/v1/semesters", headers=headers, json=semesters_payload)
    print(f"   Semesters: Status {r.status_code}")

    semesters_data = client.get(f"{SUPABASE_URL}/rest/v1/semesters?select=*", headers=headers).json()
    sem_map = {s["semester_number"]: s["id"] for s in semesters_data}

    # 3. Seed Subjects
    print("3. Seeding Subjects...")
    subject_sem_mapping = {
        "CS301": 3,
        "CS302": 3,
        "CS303": 3,
        "CS401": 4,
    }
    subjects_payload = [
        {
            "semester_id": sem_map[subject_sem_mapping[sub["subject_code"]]],
            "subject_code": sub["subject_code"],
            "subject_name": sub["subject_name"],
            "is_active": True,
        }
        for sub in SEED_SUBJECTS
        if sub["subject_code"] in subject_sem_mapping and subject_sem_mapping[sub["subject_code"]] in sem_map
    ]
    r = client.post(f"{SUPABASE_URL}/rest/v1/subjects", headers=headers, json=subjects_payload)
    print(f"   Subjects: Status {r.status_code}")

    subjects_data = client.get(f"{SUPABASE_URL}/rest/v1/subjects?select=*", headers=headers).json()
    sub_map = {s["subject_code"]: s["id"] for s in subjects_data}

    # 4. Seed Experiments
    print("4. Seeding Experiments...")
    exp_code_mapping = {
        "exp-cn-1": "CS301",
        "exp-cn-2": "CS301",
        "exp-dbms-1": "CS302",
        "exp-java-1": "CS303",
        "exp-os-1": "CS401",
    }
    experiments_payload = [
        {
            "subject_id": sub_map[exp_code_mapping[exp["id"]]],
            "experiment_number": exp["experiment_number"],
            "title": exp["title"],
            "description": exp["description"],
            "is_published": True,
        }
        for exp in SEED_EXPERIMENTS
        if exp_code_mapping[exp["id"]] in sub_map
    ]
    r = client.post(f"{SUPABASE_URL}/rest/v1/experiments", headers=headers, json=experiments_payload)
    print(f"   Experiments: Status {r.status_code}")

    experiments_data = client.get(f"{SUPABASE_URL}/rest/v1/experiments?select=*", headers=headers).json()
    exp_db_map = {(e["subject_id"], e["experiment_number"]): e["id"] for e in experiments_data}

    # 5. Upload source files to Supabase Storage and seed Experiment Versions
    print("5. Uploading Source Files to Storage bucket 'programs'...")
    for exp in SEED_EXPERIMENTS:
        filename = exp["filename"]
        content = DEMO_PROGRAMS[filename].encode("utf-8")
        sha256 = get_demo_hash(filename)
        storage_path = f"programs/{filename}"

        # Upload file to storage
        upload_url = f"{SUPABASE_URL}/storage/v1/object/programs/{filename}"
        upload_headers = {
            "apikey": SECRET_KEY,
            "Authorization": f"Bearer {SECRET_KEY}",
            "x-upsert": "true",
        }
        res = client.post(upload_url, headers=upload_headers, files={"file": (filename, content)})
        print(f"   Uploaded {filename}: Status {res.status_code}")

        # Insert version
        sub_id = sub_map[exp_code_mapping[exp["id"]]]
        exp_id = exp_db_map.get((sub_id, exp["experiment_number"]))
        if exp_id:
            ver_payload = [
                {
                    "experiment_id": exp_id,
                    "version_number": 1,
                    "storage_path": storage_path,
                    "filename": filename,
                    "sha256": sha256,
                }
            ]
            v_res = client.post(f"{SUPABASE_URL}/rest/v1/experiment_versions", headers=headers, json=ver_payload)
            print(f"   Version for {exp['title']}: Status {v_res.status_code}")

print("\n✨ Supabase Catalog Publishing Complete!")
