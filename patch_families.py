with open("frontend/src/pages/Memories/MemoriesPage.tsx", "r") as f:
    mem = f.read()

mem = mem.replace("const { currentFamily } = useAuth();\n  const currentFamilyId = currentFamily?.id;", """  const [currentFamilyId, setCurrentFamilyId] = useState<string | null>(null);
  
  useEffect(() => {
    // Fetch families and set first as active for this prototype
    fetch('/api/v1/families', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
      .then(r => r.json())
      .then(d => {
        if (d.items && d.items.length > 0) setCurrentFamilyId(d.items[0].id);
      })
      .catch(console.error);
  }, []);""")

with open("frontend/src/pages/Memories/MemoriesPage.tsx", "w") as f:
    f.write(mem)


with open("frontend/src/pages/Memories/MemoryCreatePage.tsx", "r") as f:
    mem_c = f.read()

mem_c = mem_c.replace("const { currentFamily } = useAuth();\n  const currentFamilyId = currentFamily?.id;", """  const [currentFamilyId, setCurrentFamilyId] = useState<string | null>(null);
  
  useEffect(() => {
    fetch('/api/v1/families', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
      .then(r => r.json())
      .then(d => {
        if (d.items && d.items.length > 0) setCurrentFamilyId(d.items[0].id);
      })
      .catch(console.error);
  }, []);""")

with open("frontend/src/pages/Memories/MemoryCreatePage.tsx", "w") as f:
    f.write(mem_c)


with open("frontend/src/pages/Memories/MemoryDetailPage.tsx", "r") as f:
    mem_d = f.read()

mem_d = mem_d.replace('confirmText="Delete"\n        cancelText="Cancel"', 'confirmLabel="Delete"\n        cancelLabel="Cancel"')

with open("frontend/src/pages/Memories/MemoryDetailPage.tsx", "w") as f:
    f.write(mem_d)

