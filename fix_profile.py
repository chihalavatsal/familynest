with open("frontend/src/pages/Profile/ProfilePage.tsx", "r") as f:
    content = f.read()

# Fix the API response handling
old_load = """  const load = async () => {
    setLoadState('loading');
    try {
      const data = await profileApi.getProfile();
      if ('detail' in data) {
        setLoadState('no-person');
        return;
      }
      setProfile(data as SafePersonSummary);
      setLoadState('ready');
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      if (apiErr.status === 400) {
        setLoadState('no-person');
      } else {
        setErrorMsg(apiErr.message ?? 'Could not load profile.');
        setLoadState('error');
      }
    }
  };"""

new_load = """  const load = async () => {
    setLoadState('loading');
    try {
      const data = await profileApi.getProfile() as { user: any, person: SafePersonSummary | null, detail?: string };
      if (data.detail || !data.person) {
        setLoadState('no-person');
        return;
      }
      setProfile(data.person);
      setLoadState('ready');
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      if (apiErr.status === 400 || apiErr.status === 404) {
        setLoadState('no-person');
      } else {
        setErrorMsg(apiErr.message ?? 'Could not load profile.');
        setLoadState('error');
      }
    }
  };"""

content = content.replace(old_load, new_load)

with open("frontend/src/pages/Profile/ProfilePage.tsx", "w") as f:
    f.write(content)
