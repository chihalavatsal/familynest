import { api } from './client';
import type { MediaResponse } from '../types/media';

export const mediaApi = {
  list: (family_id: string) => api.get<MediaResponse[]>(`/media?family_id=${family_id}`),
  get: (id: string) => api.get<MediaResponse>(`/media/${id}`),
  delete: (id: string) => api.delete<void>(`/media/${id}`),
};
