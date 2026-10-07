import { api } from './client';
import type { ActivityResponse } from '../types/events';

export const activityApi = {
  list: (params?: { family_id?: string; limit?: number; offset?: number }) => {
    const q = new URLSearchParams();
    if (params?.family_id) q.append('family_id', params.family_id);
    if (params?.limit) q.append('limit', String(params.limit));
    if (params?.offset) q.append('offset', String(params.offset));
    return api.get<ActivityResponse[]>(`/activity?${q.toString()}`);
  }
};
