import re
with open("backend/app/db/models/notification.py", "r") as f:
    content = f.read()

prefs = """    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    in_app_enabled = Column(Boolean, default=True, nullable=False)
    birthdays_enabled = Column(Boolean, default=True, nullable=False)
    anniversaries_enabled = Column(Boolean, default=True, nullable=False)
    remembrance_enabled = Column(Boolean, default=True, nullable=False)
    work_anniversaries_enabled = Column(Boolean, default=True, nullable=False)"""

content = re.sub(r'    user_id = .*?\n    in_app_enabled = Column\(Boolean, default=True, nullable=False\)', prefs, content)

with open("backend/app/db/models/notification.py", "w") as f:
    f.write(content)
