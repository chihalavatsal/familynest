import re

with open("frontend/src/components/navigation/Navigation.tsx", "r") as f:
    content = f.read()

# Add unreadCount prop to Sidebar
sidebar_repl = """interface SidebarProps {
  onClose?: () => void;
  unreadCount?: number;
}

export function Sidebar({ onClose, unreadCount = 0 }: SidebarProps) {"""
content = re.sub(r"interface SidebarProps \{\n  onClose\?: \(\) => void;\n\}\n\nexport function Sidebar\(\{ onClose \}: SidebarProps\) \{", sidebar_repl, content)

# Inject unread badge in Sidebar navItems loop
sidebar_item = """              <NavLink
                to={to}
                onClick={onClose}
                className={({ isActive }) =>
                  clsx(
                    'flex items-center justify-between gap-3 px-3 py-2.5 rounded-xl text-[14px] font-medium transition-all duration-150',
                    isActive
                      ? 'bg-[#f2ebe4] text-[#92614a]'
                      : 'text-stone-600 hover:bg-stone-50 hover:text-stone-900'
                  )
                }
                aria-label={label}
              >
                <div className="flex items-center gap-3">
                  <Icon className="w-5 h-5 shrink-0" strokeWidth={2} />
                  {label}
                </div>
                {to === '/notifications' && unreadCount > 0 && (
                  <span className="bg-[#92614a] text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full min-w-[1.25rem] text-center">
                    {unreadCount > 99 ? '99+' : unreadCount}
                  </span>
                )}
              </NavLink>"""
content = re.sub(r"              <NavLink\n                to=\{to\}.*?<Icon className=\"w-5 h-5 shrink-0\" strokeWidth=\{2\} />\n                \{label\}\n              </NavLink>", sidebar_item, content, flags=re.DOTALL)

with open("frontend/src/components/navigation/Navigation.tsx", "w") as f:
    f.write(content)
