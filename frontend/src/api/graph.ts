import { api } from './client';
import type {
  KinshipResult,
  RelatedPersonListResponse,
} from '../types';

export const graphApi = {
  howRelated: (personId: string, maxDepth: number = 6) =>
    api.get<KinshipResult>(`/relationships/how-related/${personId}?max_depth=${maxDepth}`),

  getRelationshipPath: (personId: string, maxDepth: number = 6) =>
    api.get<KinshipResult>(`/relationships/path/${personId}?max_depth=${maxDepth}`),

  getDirectRelationships: (personId: string, includeHistorical: boolean = false) =>
    api.get<RelatedPersonListResponse>(`/people/${personId}/relationships?include_historical=${includeHistorical}`),

  getAncestors: (personId: string, maxDepth: number = 6) =>
    api.get<RelatedPersonListResponse>(`/people/${personId}/ancestors?max_depth=${maxDepth}`),

  getDescendants: (personId: string, maxDepth: number = 6) =>
    api.get<RelatedPersonListResponse>(`/people/${personId}/descendants?max_depth=${maxDepth}`),

  getSiblings: (personId: string) =>
    api.get<RelatedPersonListResponse>(`/people/${personId}/siblings`),
};
