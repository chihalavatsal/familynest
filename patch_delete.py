import re

def patch_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Wrap handleDelete
    handle_delete_match = re.search(r'const handleDelete = async \(id: string\) => \{\n\s+if \(!confirm\([^\)]+\)\) return;\n', content)
    if handle_delete_match:
        content = content.replace(
            handle_delete_match.group(0),
            handle_delete_match.group(0) + '    if (isSubmitting) return;\n    setIsSubmitting(true);\n    try {\n'
        )
        
        content = content.replace(
            "await api.delete(`/people/${personId}/employments/${id}`);\n    load();\n  };",
            "await api.delete(`/people/${personId}/employments/${id}`);\n      await load();\n    } finally {\n      setIsSubmitting(false);\n    }\n  };"
        )
        
        content = content.replace(
            "await api.delete(`/people/${personId}/educations/${id}`);\n    load();\n  };",
            "await api.delete(`/people/${personId}/educations/${id}`);\n      await load();\n    } finally {\n      setIsSubmitting(false);\n    }\n  };"
        )
        
    with open(filepath, 'w') as f:
        f.write(content)

patch_file('frontend/src/components/people/EmploymentList.tsx')
patch_file('frontend/src/components/people/EducationList.tsx')
