import { api } from './client';
import type { SearchResponse } from '../types';

export const searchApi = {
  globalSearch: (params: { q: string; type?: string; family_id?: string; limit?: number }) => {
    const searchParams = new URLSearchParams();
    searchParams.append('q', params.q);
    if (params.type) searchParams.append('type', params.type);
    if (params.family_id) searchParams.append('family_id', params.family_id);
    if (params.limit) searchParams.append('limit', params.limit.toString());
    
    return api.get<SearchResponse>(`/search?${searchParams.toString()}`);
  }
};
