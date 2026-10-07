export type SearchResultType = 'person' | 'family' | 'memory' | 'album' | 'event';

export interface SearchResult {
  id: string;
  type: SearchResultType;
  title: string;
  subtitle?: string;
  family_id?: string;
  family_name?: string;
  route: string;
}

export interface SearchResponse {
  items: SearchResult[];
  total: number;
}
