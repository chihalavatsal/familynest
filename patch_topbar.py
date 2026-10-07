import re

with open("frontend/src/components/navigation/Navigation.tsx", "r") as f:
    content = f.read()

replacement = """      <div className="flex items-center gap-1">
        <NavLink
          to="/notifications"
          className="relative p-2 rounded-xl text-stone-600 hover:bg-stone-50"
          aria-label={unreadCount > 0 ? `${unreadCount} unread notifications` : `Notifications`}
        >
          <Bell className="w-5 h-5" />
          {unreadCount > 0 && (
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-[#92614a] rounded-full" />
          )}
        </NavLink>
        <NavLink to="/profile" className="p-1">
          <ChevronRight className="w-0 h-0" aria-hidden="true" />
        </NavLink>
      </div>"""

content = re.sub(
    r"<div className=\"flex items-center gap-1\">.*?</div>",
    replacement,
    content,
    flags=re.DOTALL
)

with open("frontend/src/components/navigation/Navigation.tsx", "w") as f:
    f.write(content)
