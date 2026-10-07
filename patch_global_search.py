with open("frontend/src/components/navigation/Navigation.tsx", "r") as f:
    content = f.read()

content = content.replace("import { Avatar } from '../ui/Primitives';", "import { Avatar } from '../ui/Primitives';\nimport { GlobalSearch } from './GlobalSearch';")

# In Sidebar:
sidebar_header = """<div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-[#92614a] text-white flex items-center justify-center font-serif text-xl">
            F
          </div>
          <span className="font-serif text-xl tracking-tight text-stone-900">
            FamilyNest
          </span>
        </div>"""
new_sidebar_header = sidebar_header + "\n        <GlobalSearch className=\"mt-4 hidden md:block\" />"

content = content.replace(sidebar_header, new_sidebar_header)

# In TopBar:
topbar_title = """<span className="font-serif text-lg text-[#92614a]">FamilyNest</span>"""
new_topbar_title = topbar_title + "\n      <div className=\"flex-1 flex justify-end mr-4\">\n        <GlobalSearch />\n      </div>"
content = content.replace(topbar_title, new_topbar_title)

with open("frontend/src/components/navigation/Navigation.tsx", "w") as f:
    f.write(content)
