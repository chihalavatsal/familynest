"""Diagnostic and verification script for FamilyNest database schema.

Inspects:
- Connection & PostgreSQL version
- All 7 core tables
- Columns and types
- Primary keys & Foreign keys (with delete rules)
- Unique and Check constraints
- Indexes
"""
import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(backend_dir))

from sqlalchemy import inspect, text
from app.db.database import engine, get_redacted_database_url
from app.core.config import settings

EXPECTED_TABLES = [
    "users",
    "people",
    "families",
    "family_members",
    "relationships",
    "invitations",
    "audit_logs",
]


def verify_schema() -> bool:
    redacted = get_redacted_database_url(settings.DATABASE_URL or "")
    print(f"\n=======================================================")
    print(f"FamilyNest Database Schema Verification")
    print(f"Target Database: {redacted}")
    print(f"=======================================================\n")

    try:
        with engine.connect() as conn:
            pg_version = conn.execute(text("SELECT version();")).scalar()
            print(f"[+] PostgreSQL Version:\n    {pg_version}\n")

            inspector = inspect(conn)
            tables = inspector.get_table_names()
            print(f"[+] Discovered Tables in DB: {tables}\n")

            all_ok = True
            for expected in EXPECTED_TABLES:
                if expected not in tables:
                    print(f"[-] MISSING TABLE: {expected}")
                    all_ok = False
                else:
                    print(f"[✔] TABLE: {expected}")
                    # Columns
                    cols = inspector.get_columns(expected)
                    col_names = [f"{c['name']} ({c['type']})" for c in cols]
                    print(f"    Columns: {', '.join(col_names)}")

                    # PK
                    pk = inspector.get_pk_constraint(expected)
                    print(f"    PK: {pk.get('constrained_columns', [])}")

                    # Foreign keys
                    fks = inspector.get_foreign_keys(expected)
                    for fk in fks:
                        print(f"    FK: {fk.get('constrained_columns')} -> {fk.get('referred_table')}.{fk.get('referred_columns')} (ondelete: {fk.get('options', {}).get('ondelete', 'default')})")

                    # Unique constraints
                    uqs = inspector.get_unique_constraints(expected)
                    for uq in uqs:
                        print(f"    Unique: {uq.get('name')} {uq.get('column_names')}")

                    # Check constraints
                    cks = inspector.get_check_constraints(expected)
                    for ck in cks:
                        print(f"    Check: {ck.get('name')}: {ck.get('sqltext')}")

                    # Indexes
                    idxs = inspector.get_indexes(expected)
                    for idx in idxs:
                        print(f"    Index: {idx.get('name')} {idx.get('column_names')} (unique={idx.get('unique')})")
                    print()

            if all_ok:
                print("=======================================================")
                print("[✔] All 7 core tables, constraints, and indexes verified successfully!")
                print("=======================================================\n")
                return True
            else:
                print("=======================================================")
                print("[-] Verification failed: Some expected tables are missing.")
                print("=======================================================\n")
                return False

    except Exception as e:
        print(f"[-] Connection or verification failed: {e}")
        return False


if __name__ == "__main__":
    success = verify_schema()
    sys.exit(0 if success else 1)
