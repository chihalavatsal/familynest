with open("frontend/src/components/navigation/Sidebar.tsx", "r") as f:
    content = f.read()

memories_nav = """  { icon: Heart, label: 'Relationships', path: '/relationships' },
  { icon: BookOpen, label: 'Memories', path: '/memories' },"""

content = content.replace("  { icon: Heart, label: 'Relationships', path: '/relationships' },", memories_nav)

with open("frontend/src/components/navigation/Sidebar.tsx", "w") as f:
    f.write(content)
