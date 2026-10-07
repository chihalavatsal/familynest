with open("frontend/src/pages/Tree/FamilyTreePage.tsx", "r") as f:
    code = f.read()

import re

# We will completely replace the fetching logic with useQuery
new_logic = """
  const { data: dashboard } = useQuery({ 
    queryKey: ['dashboard'], 
    queryFn: profileApi.getDashboard,
    staleTime: 1000 * 60 * 5
  });
  
  const myProfile = dashboard?.profile || null;
  const targetId = personIdParam || myProfile?.id;

  const { data: centerPerson, isLoading: isPersonLoading, error: personError } = useQuery({
    queryKey: ['person', targetId],
    queryFn: () => targetId ? peopleApi.get(targetId) : Promise.reject('No ID'),
    enabled: !!targetId,
    staleTime: 1000 * 60 * 5
  });

  const { data: relationships = [], isLoading: isRelLoading } = useQuery({
    queryKey: ['relationships', targetId],
    queryFn: () => targetId ? graphApi.getDirectRelationships(targetId, true) : Promise.resolve([]),
    enabled: !!targetId,
    refetchInterval: 5000, // Real-time polling
    staleTime: 1000 * 60 * 5
  });

  const isLoading = (!dashboard && !myProfile) || isPersonLoading || isRelLoading;
  
  // We can derive loadState for the UI
  let loadState: 'loading' | 'error' | 'ready' | 'onboarding' = 'ready';
  if (isLoading && !centerPerson) loadState = 'loading';
  else if (!targetId && !isLoading) loadState = 'onboarding';
  else if (personError) loadState = 'error';

"""

# We need to remove the old state and initialize function
code = re.sub(r'const \[centerPerson, setCenterPerson\] = useState.*?const \[relationships, setRelationships\] = useState<RelatedPersonItem\[\]>\(\[\]\);', '', code, flags=re.DOTALL)
code = re.sub(r'const \[loadState, setLoadState\] = useState.*?;', '', code, flags=re.DOTALL)
code = re.sub(r'const \[errorMsg, setErrorMsg\] = useState\(\'\'\);', '', code, flags=re.DOTALL)
code = re.sub(r'const initialize = useCallback.*?\}, \[initialize\]\);', new_logic, code, flags=re.DOTALL)

# Fix references
code = code.replace("errorMsg", "String(personError)")

with open("frontend/src/pages/Tree/FamilyTreePage.tsx", "w") as f:
    f.write(code)
