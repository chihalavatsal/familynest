import { api } from './client';
import type { InvitationListResponse, InvitationResponse, PersonClaimResponse } from '../types';

export const invitationsApi = {
  list: (direction?: 'sent' | 'received') => {
    const params = direction ? `?direction=${direction}` : '';
    return api.get<InvitationListResponse>(`/invitations${params}`);
  },

  get: (id: string) => api.get<InvitationResponse>(`/invitations/${id}`),

  acceptById: (id: string) => api.post<PersonClaimResponse>(`/invitations/${id}/accept`),

  cancel: (id: string) => api.post<InvitationResponse>(`/invitations/${id}/cancel`),
};
