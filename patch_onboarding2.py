import re

with open("frontend/src/pages/Dashboard/OnboardingPrompt.tsx", "r") as f:
    content = f.read()

old_func = """  const handleCreateProfile = async (values: any) => {
    try {
      // Strip empty strings to prevent Pydantic 422 errors on Optional[date] etc
      const payload = Object.fromEntries(
        Object.entries(values).filter(([_, v]) => v !== '' && v !== null && v !== undefined)
      );
      await profileApi.completeOnboarding(payload);"""

new_func = """  const handleCreateProfile = async (values: any) => {
    try {
      await profileApi.completeOnboarding(values);"""

content = content.replace(old_func, new_func)

with open("frontend/src/pages/Dashboard/OnboardingPrompt.tsx", "w") as f:
    f.write(content)
