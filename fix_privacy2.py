import re
with open("frontend/src/pages/Privacy/PrivacyPage.tsx", "r") as f:
    content = f.read()

content = content.replace("<OnboardingPrompt />", "<OnboardingPrompt onComplete={() => window.location.reload()} />")

with open("frontend/src/pages/Privacy/PrivacyPage.tsx", "w") as f:
    f.write(content)
