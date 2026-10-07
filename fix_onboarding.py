import re

# 1. Update ProfilePage.tsx to pass onComplete={load}
with open("frontend/src/pages/Profile/ProfilePage.tsx", "r") as f:
    content = f.read()

content = content.replace("<OnboardingPrompt />", "<OnboardingPrompt onComplete={load} />")
with open("frontend/src/pages/Profile/ProfilePage.tsx", "w") as f:
    f.write(content)

# 2. Update OnboardingPrompt.tsx
with open("frontend/src/pages/Dashboard/OnboardingPrompt.tsx", "r") as f:
    content = f.read()

content = content.replace("export function OnboardingPrompt() {", "export function OnboardingPrompt({ onComplete }: { onComplete?: () => void }) {")
content = content.replace("const { load, user } = useAuth();", "const { user } = useAuth();")
content = content.replace("load(); // Reloads auth context", "if (onComplete) onComplete();")
content = content.replace("load();", "if (onComplete) onComplete();")
content = content.replace("import { useState, useEffect } from 'react';", "import { useState } from 'react';")
content = content.replace("await invitationsApi.accept(inv.token);", "await invitationsApi.acceptById(inv.id);")

with open("frontend/src/pages/Dashboard/OnboardingPrompt.tsx", "w") as f:
    f.write(content)
