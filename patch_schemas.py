import glob

for fpath in glob.glob("backend/app/schemas/*.py"):
    with open(fpath, "r") as f:
        content = f.read()
    if "SafePersonSummary" in content:
        content = content.replace("SafePersonSummary", "PersonListItem")
        with open(fpath, "w") as f:
            f.write(content)
