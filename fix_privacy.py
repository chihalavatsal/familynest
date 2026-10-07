import re
with open("frontend/src/pages/Privacy/PrivacyPage.tsx", "r") as f:
    content = f.read()

# Make sure OnboardingPrompt is imported
if "import { OnboardingPrompt }" not in content:
    content = content.replace("import { ListSkeleton } from '../../components/feedback';", "import { ListSkeleton } from '../../components/feedback';\nimport { OnboardingPrompt } from '../Dashboard/OnboardingPrompt';")

# Add noPerson state
if "const [noPerson, setNoPerson] = useState(false);" not in content:
    content = content.replace("const [loading, setLoading] = useState(true);", "const [loading, setLoading] = useState(true);\n  const [noPerson, setNoPerson] = useState(false);")

# Update catch block
old_catch = """      } catch (err: any) {
        error(err.message || 'Failed to load privacy settings');
      } finally {"""

new_catch = """      } catch (err: any) {
        if (err.message && err.message.includes("No claimed person found")) {
          setNoPerson(true);
        } else {
          error(err.message || 'Failed to load privacy settings');
        }
      } finally {"""

content = content.replace(old_catch, new_catch)

# Update useEffect dependencies to remove error to avoid loops
content = content.replace("}, [error]);", "}, []);")

# Handle render for noPerson
render_no_person = """
  if (noPerson) {
    return (
      <div className="max-w-3xl mx-auto pt-8">
        <OnboardingPrompt />
      </div>
    );
  }
"""

if "if (noPerson)" not in content:
    content = content.replace("if (loading) return", render_no_person + "\n  if (loading) return")

with open("frontend/src/pages/Privacy/PrivacyPage.tsx", "w") as f:
    f.write(content)
