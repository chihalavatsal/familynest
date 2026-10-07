with open("frontend/src/components/navigation/Navigation.tsx", "r") as f:
    content = f.read()

# Sidebar:
sidebar_logo = """            <div className="text-[10px] text-[#92614a] font-medium tracking-wider uppercase leading-none mt-0.5">
              Private & Secure
            </div>
          </div>
        </div>"""
new_sidebar = sidebar_logo + "\n        <GlobalSearch className=\"mt-4 mb-2 hidden md:block\" />"

content = content.replace(sidebar_logo, new_sidebar)

# TopBar:
topbar_logo = """      {/* Center: Title/Logo */}
      <div className="font-serif text-lg font-semibold text-stone-900 tracking-tight flex items-center gap-2">
        <Home className="w-5 h-5 text-[#92614a]" />
        FamilyNest
      </div>

      {/* Right: Actions */}"""
new_topbar = topbar_logo.replace("      {/* Right: Actions */}", "      <div className=\"flex-1 flex justify-end mr-2\"><GlobalSearch className=\"hidden sm:block\" /></div>\n      {/* Right: Actions */}")

content = content.replace(topbar_logo, new_topbar)

with open("frontend/src/components/navigation/Navigation.tsx", "w") as f:
    f.write(content)

with open("frontend/src/pages/Search/SearchResultsPage.tsx", "r") as f:
    c = f.read()
c = c.replace(", Link }", " }")
with open("frontend/src/pages/Search/SearchResultsPage.tsx", "w") as f:
    f.write(c)

