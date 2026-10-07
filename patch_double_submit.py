import re

def patch_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Add state
    if "const [isSubmitting, setIsSubmitting] = useState(false);" not in content:
        content = content.replace(
            "const [showAdd, setShowAdd] = useState(false);",
            "const [showAdd, setShowAdd] = useState(false);\n  const [isSubmitting, setIsSubmitting] = useState(false);"
        )

    # Wrap handleAdd
    handle_add_match = re.search(r'const handleAdd = async \(e: React.FormEvent\) => \{\n\s+e\.preventDefault\(\);', content)
    if handle_add_match:
        content = content.replace(
            handle_add_match.group(0),
            handle_add_match.group(0) + '\n    if (isSubmitting) return;\n    setIsSubmitting(true);\n    try {'
        )
        
        # Replace the load(); at the end with a finally block
        # This is tricky using regex, let's just do a string replace for the specific end of handleAdd.
        if "EmploymentList" in filepath:
            content = content.replace(
                "setShowAdd(false);\n    resetForm();\n    load();\n  };",
                "setShowAdd(false);\n      resetForm();\n      load();\n    } finally {\n      setIsSubmitting(false);\n    }\n  };"
            )
        else: # EducationList
            content = content.replace(
                "setEndDate('');\n    load();\n  };",
                "setEndDate('');\n      load();\n    } finally {\n      setIsSubmitting(false);\n    }\n  };"
            )

    # Disable button (Find the Save button)
    if "EmploymentList" in filepath:
        content = content.replace(
            '<Button type="submit" variant="primary" disabled={!employer || !title}>Save</Button>',
            '<Button type="submit" variant="primary" loading={isSubmitting} disabled={!employer || !title || isSubmitting}>Save</Button>'
        )
    else:
        # EducationList uses a standard button? Let's check
        pass

    with open(filepath, 'w') as f:
        f.write(content)

patch_file('frontend/src/components/people/EmploymentList.tsx')
patch_file('frontend/src/components/people/EducationList.tsx')

