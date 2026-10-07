import { api } from './client';
import type {
  EventResponse,
  EventCreatePayload,
  EventUpdatePayload,
  EventParticipantResponse,
} from '../types/events';

export const eventsApi = {
  list: (params?: { event_type?: string; upcoming?: boolean; limit?: number; offset?: number }) => {
    const q = new URLSearchParams();
    if (params?.event_type) q.append('event_type', params.event_type);
    if (params?.upcoming !== undefined) q.append('upcoming', String(params.upcoming));
    if (params?.limit) q.append('limit', String(params.limit));
    if (params?.offset) q.append('offset', String(params.offset));
    return api.get<EventResponse[]>(`/events?${q.toString()}`);
  },

  getUpcoming: (params?: { limit?: number; offset?: number }) => {
    const q = new URLSearchParams();
    if (params?.limit) q.append('limit', String(params.limit));
    if (params?.offset) q.append('offset', String(params.offset));
    return api.get<EventResponse[]>(`/events/upcoming?${q.toString()}`);
  },

  get: (eventId: string) =>
    api.get<EventResponse>(`/events/${eventId}`),

  create: (data: EventCreatePayload) =>
    api.post<EventResponse>('/events', data),

  update: (eventId: string, data: EventUpdatePayload) =>
    api.patch<EventResponse>(`/events/${eventId}`, data),

  delete: (eventId: string) =>
    api.delete<void>(`/events/${eventId}`),

  listParticipants: (eventId: string, params?: { limit?: number; offset?: number }) => {
    const q = new URLSearchParams();
    if (params?.limit) q.append('limit', String(params.limit));
    if (params?.offset) q.append('offset', String(params.offset));
    return api.get<EventParticipantResponse[]>(`/events/${eventId}/participants?${q.toString()}`);
  },

  addParticipant: (eventId: string, personId: string, participantStatus: string = 'invited') =>
    api.post<EventParticipantResponse>(`/events/${eventId}/participants?person_id=${personId}&participant_status=${participantStatus}`),

  removeParticipant: (eventId: string, personId: string) =>
    api.delete<void>(`/events/${eventId}/participants/${personId}`),
};
