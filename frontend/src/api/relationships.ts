import { api } from './client';
import type { RelationshipResponse, RelationshipCreatePayload } from '../types';

export const relationshipsApi = {
  create: (data: RelationshipCreatePayload) =>
    api.post<RelationshipResponse>('/relationships', data),
};
