import { api } from './client';
import type {
  PersonListResponse,
  PersonDetailResponse,
  PersonCreatePayload,
  PersonUpdatePayload,
  PersonClaimResponse,
  InvitationResponse,
  InvitationListResponse,
  InvitationCreatePayload,
} from '../types';

export const peopleApi = {
  list: (params?: {
    page?: number;
    page_size?: number;
    search?: string;
    sort_by?: string;
    sort_dir?: 'asc' | 'desc';
  }) => {
    const q = new URLSearchParams();
    if (params?.page) q.set('page', String(params.page));
    if (params?.page_size) q.set('page_size', String(params.page_size));
    if (params?.search) q.set('search', params.search);
    if (params?.sort_by) q.set('sort_by', params.sort_by);
    if (params?.sort_dir) q.set('sort_dir', params.sort_dir);
    const qs = q.toString();
    return api.get<PersonListResponse>(`/people${qs ? `?${qs}` : ''}`);
  },

  get: (personId: string) =>
    api.get<PersonDetailResponse>(`/people/${personId}`),

  create: (data: PersonCreatePayload) =>
    api.post<PersonDetailResponse>('/people', data),

  update: (personId: string, data: PersonUpdatePayload) =>
    api.patch<PersonDetailResponse>(`/people/${personId}`, data),

  claim: (personId: string) =>
    api.post<PersonClaimResponse>(`/people/${personId}/claim`),

  createInvitation: (personId: string, data?: InvitationCreatePayload) =>
    api.post<InvitationResponse>(`/people/${personId}/invitations`, data ?? {}),
    
  delete: (personId: string) =>
    api.delete<void>(`/people/${personId}`),
};

export const invitationsApi = {
  list: (direction?: 'sent' | 'received') => {
    const q = direction ? `?direction=${direction}` : '';
    return api.get<InvitationListResponse>(`/invitations${q}`);
  },

  get: (invitationId: string) =>
    api.get<InvitationResponse>(`/invitations/${invitationId}`),

  cancel: (invitationId: string) =>
    api.post<InvitationResponse>(`/invitations/${invitationId}/cancel`),

  accept: (token: string) =>
    api.post<PersonClaimResponse>(`/invitations/${token}/accept`),
};
