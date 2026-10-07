with open("frontend/src/components/family/FamilyForm.tsx", "r") as f:
    content = f.read()

old_btn = """        <Button type="submit" loading={loading}>
          {submitLabel}
        </Button>"""

new_btn = """        <Button type="submit" loading={loading}>
          {loading && isCreate ? 'Creating...' : loading ? 'Saving...' : submitLabel}
        </Button>"""

content = content.replace(old_btn, new_btn)

with open("frontend/src/components/family/FamilyForm.tsx", "w") as f:
    f.write(content)
