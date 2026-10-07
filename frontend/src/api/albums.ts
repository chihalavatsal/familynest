import { api } from './client';
import type { AlbumResponse, AlbumDetailResponse } from '../types/media';

export const albumsApi = {
  list: (family_id: string) => api.get<AlbumResponse[]>(`/albums?family_id=${family_id}`),
  get: (id: string) => api.get<AlbumDetailResponse>(`/albums/${id}`),
  create: (data: { family_id: string; title: string; description?: string }) => api.post<AlbumResponse>('/albums', data),
  update: (id: string, data: { title?: string; description?: string }) => api.patch<AlbumResponse>(`/albums/${id}`, data),
  delete: (id: string) => api.delete<void>(`/albums/${id}`),
};
