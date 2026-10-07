import glob

for fpath in glob.glob("backend/app/**/*.py", recursive=True):
    with open(fpath, "r") as f:
        content = f.read()
    if "SafePersonSummary" in content:
        content = content.replace("SafePersonSummary", "PersonListItem")
        with open(fpath, "w") as f:
            f.write(content)
