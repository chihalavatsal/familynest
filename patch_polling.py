import re
with open("frontend/src/pages/Tree/FamilyTreePage.tsx", "r") as f:
    code = f.read()

# Modify the useEffect to add a 5 second polling interval
new_effect = """  useEffect(() => {
    initialize();
    
    // Auto-refresh the tree every 5 seconds for real-time collaboration
    const intervalId = setInterval(() => {
      // Don't set loadState to 'loading' here so we don't flash the screen!
      // Just silently refetch in the background
      initialize(true); 
    }, 5000);
    
    return () => clearInterval(intervalId);
  }, [initialize]);"""

code = re.sub(r'  useEffect\(\(\) => \{\n    initialize\(\);\n  \}, \[initialize\]\);', new_effect, code)

# We need to modify initialize to accept a silent boolean
code = code.replace("const initialize = useCallback(async () => {", "const initialize = useCallback(async (silent = false) => {")
code = code.replace("setLoadState('loading');", "if (!silent) setLoadState('loading');")

with open("frontend/src/pages/Tree/FamilyTreePage.tsx", "w") as f:
    f.write(code)
