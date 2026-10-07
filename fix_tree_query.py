with open("frontend/src/pages/Tree/FamilyTreePage.tsx", "r") as f:
    code = f.read()

import re

# Fix queryFn and relationships mapping
code = code.replace(
    "const { data: relationships = [], isLoading: isRelLoading, refetch: refetchRel } = useQuery({",
    "const { data: relResponse, isLoading: isRelLoading, refetch: refetchRel } = useQuery({"
)
code = code.replace(
    "queryFn: () => targetId ? graphApi.getDirectRelationships(targetId, true) : Promise.resolve([]),",
    "queryFn: () => targetId ? graphApi.getDirectRelationships(targetId, true) : Promise.resolve({ items: [], total: 0 }),"
)

# Extract relationships array from response
if "const relationships = relResponse?.items || [];" not in code:
    code = code.replace("  const isLoading = (!dashboard", "  const relationships = relResponse?.items || [];\n  const isLoading = (!dashboard")

# Clean up unused imports
code = code.replace("import type { PersonDetailResponse, RelatedPersonItem, SafePersonSummary, ApiError } from '../../types';", "import type { RelatedPersonItem } from '../../types';")

with open("frontend/src/pages/Tree/FamilyTreePage.tsx", "w") as f:
    f.write(code)
