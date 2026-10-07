import re
with open("frontend/src/components/navigation/Navigation.tsx", "r") as f:
    content = f.read()

navItems_regex = r"const navItems = \[.*?\];"
new_navItems = """const navItems = [
  { to: '/dashboard', icon: Home, label: 'Dashboard' },
  { to: '/people', icon: Users, label: 'People' },
  { to: '/tree', icon: Network, label: 'Family Tree' },
  { to: '/families', icon: Users, label: 'Families' },
  { to: '/events', icon: Calendar, label: 'Events' },
  { to: '/activity', icon: Activity, label: 'Activity' },
  { to: '/notifications', icon: Bell, label: 'Notifications' },
  { to: '/invitations', icon: Mail, label: 'Invitations' },
];"""

content = re.sub(navItems_regex, new_navItems, content, flags=re.DOTALL)

with open("frontend/src/components/navigation/Navigation.tsx", "w") as f:
    f.write(content)
