import { api } from './client';
import type {
  FamilyListResponse,
  FamilyResponse,
  FamilyCreatePayload,
  FamilyUpdatePayload,
  FamilyMemberListResponse,
  FamilyMemberResponse,
  FamilyOverview,
} from '../types';

export const familiesApi = {
  list: (params?: { page?: number; page_size?: number }) => {
    const q = new URLSearchParams();
    if (params?.page) q.set('page', String(params.page));
    if (params?.page_size) q.set('page_size', String(params.page_size));
    const qs = q.toString();
    return api.get<FamilyListResponse>(`/families${qs ? `?${qs}` : ''}`);
  },

  get: (familyId: string) =>
    api.get<FamilyResponse>(`/families/${familyId}`),

  create: (data: FamilyCreatePayload) =>
    api.post<FamilyResponse>('/families', data),

  update: (familyId: string, data: FamilyUpdatePayload) =>
    api.patch<FamilyResponse>(`/families/${familyId}`, data),

  delete: (familyId: string) =>
    api.delete<void>(`/families/${familyId}`),

  getOverview: (familyId: string) =>
    api.get<FamilyOverview>(`/families/${familyId}/overview`),

  // Members
  listMembers: (familyId: string, params?: { page?: number; page_size?: number }) => {
    const q = new URLSearchParams();
    if (params?.page) q.set('page', String(params.page));
    if (params?.page_size) q.set('page_size', String(params.page_size));
    const qs = q.toString();
    return api.get<FamilyMemberListResponse>(
      `/families/${familyId}/members${qs ? `?${qs}` : ''}`
    );
  },

  addMember: (familyId: string, personId: string, role: string = 'member') =>
    api.post<FamilyMemberResponse>(`/families/${familyId}/members`, {
      person_id: personId,
      role,
    }),

  updateMemberRole: (familyId: string, personId: string, role: string) =>
    api.patch<FamilyMemberResponse>(`/families/${familyId}/members/${personId}`, {
      role,
    }),

  removeMember: (familyId: string, personId: string) =>
    api.delete<void>(`/families/${familyId}/members/${personId}`),
};
