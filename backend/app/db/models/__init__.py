"""FamilyNest Database Models

Core Architecture Rule:
A USER is not the same thing as a PERSON.
A person can exist without an account (e.g. an unclaimed family member).
Later, a user can claim that existing person record.

Core Entities planned for future phases:
- users: Authentication accounts, credentials, status
- people: Human identity records (living or deceased, claimed or unclaimed)
- families: Family network hubs (a person can belong to multiple family networks)
- family_members: Associations linking people to family networks with roles
- relationships: Fundamental relationships (parent, child, spouse, divorced_spouse, sibling, guardian)
- invitations: Family network and account claim invitations
- audit_logs: Tracking changes and privacy actions
"""

from app.db.database import Base

__all__ = ["Base"]
