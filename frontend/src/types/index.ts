export * from './events';

/**
 * FamilyNest Domain Types
 *
 * Architecture rules:
 * 1. User ≠ Person. A Person can exist without an account.
 * 2. A User can claim exactly one Person.
 * 3. A Person can belong to multiple Family networks.
 * 4. Derived relationships are calculated server-side; never duplicated in frontend.
 * 5. Privacy is enforced by the backend; frontend renders what it receives.
 */

// ============================================================
// AUTH
// ============================================================

export interface AuthUser {
  id: string;
  email: string;
  display_name: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  display_name?: string;
}

// ============================================================
// PERSON & PRIVACY
// ============================================================

export type ProfileStatus = 'unclaimed' | 'claimed' | 'invited' | 'deceased';

// Summary used in list responses (no phone/email per backend privacy rules)
export interface PersonListItem {
  id: string;
  first_name: string;
  middle_name?: string | null;
  last_name?: string | null;
  nickname?: string | null;
  gender?: string | null;
  date_of_birth?: string | null;
  is_deceased: boolean;
  is_minor: boolean;
  profile_status: ProfileStatus;
  profile_photo_url?: string | null;
  occupation?: string | null;
  current_city?: string | null;
  created_by_user_id?: string | null;
  created_at: string;
  updated_at: string;
}

// Full detail response (may include phone/email for creator)
export interface PersonDetailResponse {
  id: string;
  first_name: string;
  middle_name?: string | null;
  last_name?: string | null;
  nickname?: string | null;
  gender?: string | null;
  date_of_birth?: string | null;
  date_of_death?: string | null;
  death_place?: string | null;
  birth_place?: string | null;
  current_city?: string | null;
  occupation?: string | null;
  bio?: string | null;
  profile_photo_url?: string | null;
  phone?: string | null;
  email?: string | null;
  is_deceased: boolean;
  is_minor: boolean;
  profile_status: ProfileStatus;
  created_by_user_id?: string | null;
  claimed_by_user_id?: string | null;
  created_at: string;
  updated_at: string;
}

export interface PersonListResponse {
  items: PersonListItem[];
  page: number;
  page_size: number;
  total: number;
}

export interface PersonCreatePayload {
  first_name: string;
  middle_name?: string;
  last_name?: string;
  nickname?: string;
  gender?: string;
  date_of_birth?: string;
  date_of_death?: string;
  death_place?: string;
  birth_place?: string;
  current_city?: string;
  occupation?: string;
  bio?: string;
  profile_photo_url?: string;
  phone?: string;
  email?: string;
  is_deceased?: boolean;
  is_minor?: boolean;
  profile_status?: ProfileStatus;
}

export type PersonUpdatePayload = Partial<PersonCreatePayload>;

// Safe subset used inside graph/dashboard (may have privacy-redacted nulls)
export interface SafePersonSummary {
  id: string;
  first_name: string;
  middle_name?: string | null;
  last_name?: string | null;
  nickname?: string | null;
  gender?: string | null;
  is_deceased: boolean;
  is_minor: boolean;
  profile_status: ProfileStatus;
  date_of_birth?: string | null;
  date_of_death?: string | null;
  death_place?: string | null;
  birth_place?: string | null;
  current_city?: string | null;
  occupation?: string | null;
  bio?: string | null;
  profile_photo_url?: string | null;
  phone?: string | null;
  email?: string | null;
}

export type VisibilityLevel = 'private' | 'family' | 'public';

export interface PrivacySettings {
  phone_visibility: VisibilityLevel;
  email_visibility: VisibilityLevel;
  dob_visibility: VisibilityLevel;
  bio_visibility: VisibilityLevel;
}

export interface ProfileCompletenessResponse {
  percentage: number;
  completed: string[];
  missing: string[];
}

export interface PersonProfileUpdate {
  first_name?: string;
  middle_name?: string;
  last_name?: string;
  nickname?: string;
  gender?: string;
  date_of_birth?: string;
  birth_place?: string;
  current_city?: string;
  occupation?: string;
  bio?: string;
  phone?: string;
  email?: string;
  profile_photo_url?: string;
}

// ============================================================
// FAMILY
// ============================================================

export type FamilyRole = 'owner' | 'admin' | 'member' | 'invited';

export interface FamilyListItem {
  id: string;
  name: string;
  description?: string | null;
  created_by_user_id: string;
  created_at: string;
  updated_at: string;
  member_count: number;
}

export interface FamilyResponse {
  id: string;
  name: string;
  description?: string | null;
  created_by_user_id: string;
  created_at: string;
  updated_at: string;
  member_count: number;
}

export interface FamilyListResponse {
  items: FamilyListItem[];
  page: number;
  page_size: number;
  total: number;
}

export interface FamilyMemberResponse {
  person_id: string;
  family_id: string;
  role: FamilyRole;
  joined_at?: string | null;
  created_at: string;
  // Safe person fields
  first_name: string;
  last_name?: string | null;
  nickname?: string | null;
  profile_photo_url?: string | null;
  profile_status: ProfileStatus;
}

export interface FamilyMemberListResponse {
  items: FamilyMemberResponse[];
  page: number;
  page_size: number;
  total: number;
}

export interface FamilyCreatePayload {
  name: string;
  description?: string;
}

export interface FamilyUpdatePayload {
  name?: string;
  description?: string;
}

// Used in dashboard profile summary (from profile.py)
export interface FamilySummary {
  id: string;
  name: string;
  role: FamilyRole;
  member_count: number;
}

export interface FamilyOverview {
  id: string;
  name: string;
  member_count: number;
  upcoming_events: EventItem[];
  recent_activity: ActivityItem[];
}

// ============================================================
// INVITATIONS
// ============================================================

export type InvitationStatus = 'pending' | 'accepted' | 'expired' | 'cancelled';

export interface InvitationResponse {
  id: string;
  family_id?: string | null;
  person: SafePersonSummary;
  invited_by_user_id: string;
  invited_email?: string | null;
  invited_phone?: string | null;
  invitation_type: string;
  status: InvitationStatus;
  expires_at?: string | null;
  created_at: string;
}

export interface InvitationListResponse {
  items: InvitationResponse[];
  total: number;
}

export interface PersonClaimResponse {
  person: SafePersonSummary;
  claimed: boolean;
}

export interface InvitationCreatePayload {
  invited_email?: string;
  invited_phone?: string;
  invitation_type?: string;
}

// ============================================================
// EVENTS
// ============================================================

export type EventType =
  | 'birthday'
  | 'anniversary'
  | 'important_date'
  | 'family_event'
  | 'announcement';

export type EventStatus = 'upcoming' | 'ongoing' | 'past' | 'cancelled';

export interface EventItem {
  id: string;
  event_type: EventType;
  title: string;
  description?: string | null;
  start_datetime?: string | null;
  end_datetime?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  all_day: boolean;
  status: EventStatus;
  person_id?: string | null;
  created_by_user_id: string;
  created_at: string;
  updated_at: string;
}

// ============================================================
// ACTIVITY
// ============================================================

export type ActivityType = string;
export type EntityType = 'event' | 'family' | 'person' | 'relationship' | 'invitation';

export interface ActivityItem {
  id: string;
  activity_type: ActivityType;
  entity_type: EntityType;
  entity_id: string;
  actor_user_id: string;
  family_id?: string | null;
  metadata?: Record<string, unknown> | null;
  created_at: string;
}

// ============================================================
// NOTIFICATIONS
// ============================================================

export type NotificationAudienceType = 'family' | 'selected_members' | 'user';

export type NotificationTargetType = "family" | "person" | "user" | null;

export interface NotificationResponse {
  id: string;
  notification_type: string;
  title: string;
  body: string;
  is_read: boolean;
  created_at: string;
  target_type?: NotificationTargetType;
  target_id?: string | null;
}

export interface NotificationListResponse {
  items: NotificationResponse[];
  total: number;
  page: number;
  page_size: number;
}


export interface NotificationSummary {
  unread_count: number;
  recent: Array<Record<string, unknown>>;
}

// ============================================================
// DASHBOARD
// ============================================================

export interface RelationshipSummary {
  parents_count: number;
  children_count: number;
  siblings_count: number;
  spouses_count: number;
}

export interface DashboardResponse {
  profile: SafePersonSummary | null;
  families: FamilySummary[];
  upcoming_events: EventItem[];
  notifications: NotificationSummary;
  recent_activity: ActivityItem[];
  relationship_summary: RelationshipSummary;
}

// ============================================================
// API ERRORS
// ============================================================

export interface ApiError {
  status: number;
  message: string;
  detail?: string | Record<string, unknown>;
  fieldErrors?: Record<string, string>;
}

// ============================================================
// RELATIONSHIP GRAPH
// ============================================================

export interface RelationshipPathNode {
  person: SafePersonSummary;
  relationship: string;
}

export interface KinshipResult {
  source_person: SafePersonSummary;
  target_person: SafePersonSummary;
  relationship?: string | null;
  distance: number;
  path: RelationshipPathNode[];
}

export interface RelatedPersonItem {
  person: SafePersonSummary;
  relationship?: string | null;
  distance: number;
  path: RelationshipPathNode[];
}

export interface RelatedPersonListResponse {
  items: RelatedPersonItem[];
  total: number;
}

export * from './media';
export * from './privacy';
export * from './search';

export interface RelationshipCreatePayload {
  person_a_id: string;
  person_b_id: string;
  relationship_type: 'parent' | 'child' | 'spouse' | 'divorced_spouse' | 'sibling' | 'guardian';
  start_date?: string | null;
  end_date?: string | null;
  is_current?: boolean;
}

export interface RelationshipResponse {
  id: string;
  person_a_id: string;
  person_b_id: string;
  relationship_type: string;
  is_current: boolean;
  start_date: string | null;
  end_date: string | null;
  created_at: string;
}

export * from './timeline';
