export interface MediaResponse {
  id: string;
  family_id: string;
  uploaded_by_user_id: string | null;
  access_url: string | null;
  original_filename: string;
  mime_type: string;
  file_size: number | null;
  width: number | null;
  height: number | null;
  status: string;
  created_at: string;
  updated_at: string;
  tagged_people: Array<any>;
}

export interface AlbumResponse {
  id: string;
  family_id: string;
  title: string;
  description: string | null;
  created_by_user_id: string | null;
  created_at: string;
  updated_at: string;
  media_count: number;
}

export interface AlbumDetailResponse extends AlbumResponse {
  media: MediaResponse[];
}

export interface MemoryResponse {
  id: string;
  family_id: string;
  title: string;
  body: string;
  memory_date: string | null;
  created_by_user_id: string | null;
  created_at: string;
  updated_at: string;
  tagged_people: Array<any>;
  media: MediaResponse[];
}
