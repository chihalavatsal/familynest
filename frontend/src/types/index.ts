/**
 * Core FamilyNest Domain Types
 * 
 * Key Architecture Principles:
 * 1. A USER is NOT the same thing as a PERSON.
 *    A person can exist without an account (unclaimed family member).
 *    Later, a user can claim that existing person record.
 * 2. A Person can belong to multiple family networks.
 * 3. Fundamental relationships are stored; derived relationships are calculated.
 * 4. Relationships preserve historical records (no destructive updates).
 */

export interface User {
  id: string;
  email: string;
  isActive: boolean;
  isSuperuser: boolean;
  claimedPersonId?: string | null;
  createdAt: string;
  updatedAt: string;
}

export type Gender = 'male' | 'female' | 'other' | 'unknown';

export interface Person {
  id: string;
  firstName: string;
  lastName: string;
  maidenName?: string | null;
  gender: Gender;
  isLiving: boolean;
  dateOfBirth?: string | null;
  dateOfDeath?: string | null;
  claimedByUserId?: string | null;
  avatarUrl?: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface Family {
  id: string;
  name: string;
  description?: string | null;
  creatorPersonId: string;
  createdAt: string;
  updatedAt: string;
}

export type FamilyRole = 'admin' | 'member' | 'contributor' | 'viewer';

export interface FamilyMember {
  id: string;
  familyId: string;
  personId: string;
  role: FamilyRole;
  joinedAt: string;
}

export type RelationshipType = 
  | 'parent'
  | 'child'
  | 'spouse'
  | 'divorced_spouse'
  | 'sibling'
  | 'guardian';

export interface Relationship {
  id: string;
  personId: string;
  relatedPersonId: string;
  type: RelationshipType;
  startDate?: string | null;
  endDate?: string | null;
  isCurrent: boolean;
  notes?: string | null;
  createdAt: string;
}
