import { api } from './client';
import type { FamilyPrivacySettingsResponse, FamilyPrivacySettingsUpdate, PersonPrivacySettingsResponse, PersonPrivacySettingsUpdate } from '../types';

export const privacyApi = {
  getProfilePrivacy: () => api.get<PersonPrivacySettingsResponse>('/profile/privacy'),
  updateProfilePrivacy: (data: PersonPrivacySettingsUpdate) => api.patch<PersonPrivacySettingsResponse>('/profile/privacy', data),
  getFamilySettings: (family_id: string) => api.get<FamilyPrivacySettingsResponse>(`/families/${family_id}/settings`),
  updateFamilySettings: (family_id: string, data: FamilyPrivacySettingsUpdate) => api.patch<FamilyPrivacySettingsResponse>(`/families/${family_id}/settings`, data),
};
