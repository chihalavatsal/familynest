with open("frontend/src/pages/Memories/MemoryCreatePage.tsx", "r") as f:
    content = f.read()

content = content.replace("const [memoryDate, setMemoryDate] = useState('');", "const [memoryDate, setMemoryDate] = useState('');\n  const [visibility, setVisibility] = useState('family');")
content = content.replace("memory_date: memoryDate || undefined", "memory_date: memoryDate || undefined,\n        visibility: visibility")

html_insert = """
        <div>
          <label className="block text-sm font-medium text-stone-700 mb-1">Audience</label>
          <select
            value={visibility}
            onChange={(e) => setVisibility(e.target.value)}
            className="w-full rounded-md border-stone-300 shadow-sm focus:border-[#92614a] focus:ring-[#92614a] sm:text-sm"
          >
            <option value="family">Entire Family</option>
            <option value="selected_members">Selected Members Only (Backend enforced)</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-stone-700 mb-1">Story</label>"""

content = content.replace("<div>\n          <label className=\"block text-sm font-medium text-stone-700 mb-1\">Story</label>", html_insert)

with open("frontend/src/pages/Memories/MemoryCreatePage.tsx", "w") as f:
    f.write(content)
