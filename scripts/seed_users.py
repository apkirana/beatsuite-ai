#!/usr/bin/env python3
"""
Create the initial user accounts.

Accounts are no longer committed to the repository. This script writes
backend/data/users.json with freshly generated passwords and prints them
once — copy them into a password manager, because they are not recoverable
afterwards (only salted PBKDF2 hashes are stored).

Usage:
    python scripts/seed_users.py                 # generate random passwords
    python scripts/seed_users.py --force         # overwrite an existing file
"""

import argparse
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.auth import password as password_utils  # noqa: E402

DATA_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'backend', 'data', 'users.json')
)

# Roles to create. Names and contact details are deliberately placeholders —
# do not put real staff or patient details in a file you may commit.
SEED_ACCOUNTS = [
    {"user_id": "U001", "username": "admin",   "role": "admin",  "full_name": "Demo Administrator"},
    {"user_id": "U002", "username": "nurse1",  "role": "nurse",  "full_name": "Demo Nurse One"},
    {"user_id": "U003", "username": "nurse2",  "role": "nurse",  "full_name": "Demo Nurse Two"},
    {"user_id": "U004", "username": "family1", "role": "family", "full_name": "Demo Family Member"},
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed initial user accounts.")
    parser.add_argument('--force', action='store_true',
                        help='overwrite backend/data/users.json if it already exists')
    args = parser.parse_args()

    if os.path.exists(DATA_FILE) and not args.force:
        print(f"Refusing to overwrite existing {DATA_FILE}\nRe-run with --force if that is what you want.")
        return 1

    now = datetime.now().isoformat()
    users, printed = [], []

    for account in SEED_ACCOUNTS:
        plaintext = password_utils.generate_password()
        users.append({
            **account,
            "password_hash": password_utils.hash_password(plaintext),
            "email": f"{account['username']}@example.invalid",
            "created_at": now,
            "is_active": True,
        })
        printed.append((account['username'], account['role'], plaintext))

    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as handle:
        json.dump(users, handle, indent=2)
    os.chmod(DATA_FILE, 0o600)

    print(f"Wrote {len(users)} accounts to {DATA_FILE}\n")
    print("Save these now — they are shown once and cannot be recovered:\n")
    width = max(len(u) for u, _, _ in printed)
    for username, role, plaintext in printed:
        print(f"  {username.ljust(width)}  ({role})  {plaintext}")
    print("\nChange them after first login. This file is gitignored — keep it that way.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
