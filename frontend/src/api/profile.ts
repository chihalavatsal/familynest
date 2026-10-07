import { api } from './client';
import type {
  DashboardResponse,
  SafePersonSummary,
  PrivacySettings,
  ProfileCompletenessResponse,
  PersonProfileUpdate,
  FamilyOverview,
} from '../types';

export const profileApi = {
  getProfile: () => api.get<SafePersonSummary | { detail: string }>('/profile'),

  completeOnboarding: (data: any) => api.post<import('../types').PersonListItem>('/profile/onboarding', data),

  updatePerson: (data: PersonProfileUpdate) =>
    api.patch<SafePersonSummary>('/profile/person', data),

  getPrivacy: () => api.get<PrivacySettings>('/profile/privacy'),

  updatePrivacy: (data: Partial<PrivacySettings>) =>
    api.patch<PrivacySettings>('/profile/privacy', data),

  getCompleteness: () =>
    api.get<ProfileCompletenessResponse>('/profile/completeness'),

  getDashboard: () => api.get<DashboardResponse>('/dashboard'),

  getFamilyOverview: (familyId: string) =>
    api.get<FamilyOverview>(`/families/${familyId}/overview`),
};
