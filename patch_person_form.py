import re

with open("frontend/src/components/people/PersonForm.tsx", "r") as f:
    content = f.read()

old_submit = """    setLoading(true);
    try {
      await onSubmit(values);"""

new_submit = """    setLoading(true);
    try {
      // Convert empty strings to null so Pydantic handles them correctly 
      // (especially for Optional[date] fields which reject empty strings)
      const payload = Object.fromEntries(
        Object.entries(values).map(([k, v]) => [k, v === '' ? null : v])
      );
      await onSubmit(payload);"""

content = content.replace(old_submit, new_submit)

with open("frontend/src/components/people/PersonForm.tsx", "w") as f:
    f.write(content)
