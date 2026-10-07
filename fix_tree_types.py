with open("frontend/src/pages/Tree/FamilyTreePage.tsx", "r") as f:
    code = f.read()

import re

# Fix imports
if "import { useQuery }" not in code:
    code = code.replace("import { useEffect, useState, useCallback, useMemo } from 'react';", "import { useState, useMemo } from 'react';\nimport { useQuery } from '@tanstack/react-query';")

if "import type { PersonDetailResponse" not in code:
    code = code.replace("import { RelatedListModal } from '../../components/tree/RelatedListModal';", "import { RelatedListModal } from '../../components/tree/RelatedListModal';\nimport type { PersonDetailResponse, RelatedPersonItem, SafePersonSummary, ApiError } from '../../types';")

# Fix missing initialize
# We have `isPersonLoading` and `isRelLoading`. To refetch, we need `refetchPerson` and `refetchRel`.
code = code.replace("const { data: centerPerson, isLoading: isPersonLoading, error: personError } = useQuery({", "const { data: centerPerson, isLoading: isPersonLoading, error: personError, refetch: refetchPerson } = useQuery({")
code = code.replace("const { data: relationships = [], isLoading: isRelLoading } = useQuery({", "const { data: relationships = [], isLoading: isRelLoading, refetch: refetchRel } = useQuery({")

# Add initialize function that calls refetch
code = code.replace("const isLoading = (!dashboard && !myProfile) || isPersonLoading || isRelLoading;", """const isLoading = (!dashboard && !myProfile) || isPersonLoading || isRelLoading;

  const initialize = () => {
    refetchPerson();
    refetchRel();
  };
""")

# Fix implicit any in map/filter
code = code.replace("r =>", "(r: RelatedPersonItem) =>")
code = code.replace("p =>", "(p: RelatedPersonItem) =>")
code = code.replace("g =>", "(g: RelatedPersonItem) =>")
code = code.replace("s =>", "(s: RelatedPersonItem) =>")
code = code.replace("c =>", "(c: RelatedPersonItem) =>")

with open("frontend/src/pages/Tree/FamilyTreePage.tsx", "w") as f:
    f.write(code)
