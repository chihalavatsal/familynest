with open("frontend/src/types/index.ts", "r") as f:
    content = f.read()

types_to_add = """
export interface RelationshipCreatePayload {
  person_a_id: string;
  person_b_id: string;
  relationship_type: 'parent' | 'child' | 'spouse' | 'divorced_spouse' | 'sibling' | 'guardian';
  start_date?: string | null;
  end_date?: string | null;
  is_current?: boolean;
}

export interface RelationshipResponse {
  id: string;
  person_a_id: string;
  person_b_id: string;
  relationship_type: string;
  is_current: boolean;
  start_date: string | null;
  end_date: string | null;
  created_at: string;
}
"""

if "RelationshipCreatePayload" not in content:
    content += types_to_add
    with open("frontend/src/types/index.ts", "w") as f:
        f.write(content)
