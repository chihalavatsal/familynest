export interface EventAudienceInput {
  type: 'family' | 'selected_members' | 'user';
  family_id?: string | null;
  person_ids?: string[] | null;
  user_id?: string | null;
}

export interface EventParticipantInput {
  person_id: string;
  status?: 'invited' | 'accepted' | 'declined' | 'maybe';
}

export interface EventCreatePayload {
  event_type: 'birthday' | 'anniversary' | 'family_event' | 'important_date' | 'announcement';
  title: string;
  description?: string | null;
  start_datetime?: string | null;
  end_datetime?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  all_day?: boolean;
  person_id?: string | null;
  audience: EventAudienceInput;
  participants?: EventParticipantInput[] | null;
}

export interface EventUpdatePayload {
  title?: string | null;
  description?: string | null;
  start_datetime?: string | null;
  end_datetime?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  all_day?: boolean | null;
  status?: 'active' | 'cancelled' | null;
  audience?: EventAudienceInput | null;
}

export interface EventResponse {
  id: string;
  event_type: string;
  title: string;
  description?: string | null;
  start_datetime?: string | null;
  end_datetime?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  all_day: boolean;
  status: string;
  person_id?: string | null;
  created_by_user_id?: string | null;
  created_at: string;
  updated_at: string;
}

export interface EventParticipantResponse {
  id: string;
  event_id: string;
  person_id: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ActivityResponse {
  id: string;
  activity_type: string;
  entity_type: string;
  entity_id: string;
  actor_user_id?: string | null;
  family_id?: string | null;
  metadata: Record<string, any>;
  created_at: string;
}
