with open("frontend/src/types/index.ts", "r") as f:
    content = f.read()

import re

# Replace Notification
replacement = """export type NotificationTargetType = "family" | "person" | "user" | null;

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
"""

content = re.sub(
    r"export interface Notification \{.*?read_at\?: string \| null;\n\}",
    replacement,
    content,
    flags=re.DOTALL
)

# Invitation types
invitation_types = """
// ============================================================
// INVITATIONS
// ============================================================

export interface InvitationResponse {
  id: string;
  family_id: string | null;
  person: PersonSummary;
  invited_by_user_id: string;
  invited_email: string | null;
  invited_phone: string | null;
  invitation_type: string;
  status: 'pending' | 'accepted' | 'expired' | 'cancelled';
  expires_at: string | null;
  created_at: string;
}

export interface InvitationListResponse {
  items: InvitationResponse[];
  total: number;
}

export interface PersonClaimResponse {
  person: PersonSummary;
  claimed: boolean;
}
"""

if "export interface InvitationResponse" not in content:
    content += invitation_types

with open("frontend/src/types/index.ts", "w") as f:
    f.write(content)
