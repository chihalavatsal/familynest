import os

f = "backend/app/services/event_service.py"
with open(f, "r") as file:
    content = file.read()

# Replace flush() with commit() and refresh()
content = content.replace("self.db.flush()\n        return event", "self.db.commit()\n        self.db.refresh(event)\n        return event")
content = content.replace("self.db.flush()\n        return evt", "self.db.commit()\n        self.db.refresh(evt)\n        return evt")
content = content.replace("self.db.flush()", "self.db.commit()")

with open(f, "w") as file:
    file.write(content)
print("Done")
