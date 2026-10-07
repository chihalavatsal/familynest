export interface PersonPrivacySettingsResponse {
  person_id: string;
  phone_visibility: string;
  email_visibility: string;
  dob_visibility: string;
  bio_visibility: string;
}

export interface PersonPrivacySettingsUpdate {
  phone_visibility?: string;
  email_visibility?: string;
  dob_visibility?: string;
  bio_visibility?: string;
}

export interface FamilyPrivacySettingsResponse {
  family_id: string;
  allow_member_discovery: boolean;
  default_content_visibility: string;
  member_invites_role: string;
  member_management_role: string;
}

export interface FamilyPrivacySettingsUpdate {
  allow_member_discovery?: boolean;
  default_content_visibility?: string;
  member_invites_role?: string;
  member_management_role?: string;
}
