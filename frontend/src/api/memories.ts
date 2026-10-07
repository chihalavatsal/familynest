import { api } from './client';
import type { MemoryResponse } from '../types/media';

export const memoriesApi = {
  list: (family_id: string) => api.get<MemoryResponse[]>(`/memories?family_id=${family_id}`),
  get: (id: string) => api.get<MemoryResponse>(`/memories/${id}`),
  create: (data: { family_id: string; title: string; body: string; memory_date?: string; visibility?: string }) => api.post<MemoryResponse>('/memories', data),
  update: (id: string, data: { title?: string; body?: string; memory_date?: string }) => api.patch<MemoryResponse>(`/memories/${id}`, data),
  delete: (id: string) => api.delete<void>(`/memories/${id}`),
};
