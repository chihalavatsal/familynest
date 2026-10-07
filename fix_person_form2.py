with open("frontend/src/components/people/PersonForm.tsx", "r") as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if "initialValues?: PersonDetailResponse;" in line:
        skip = True
        new_lines.append("export interface PersonFormProps {\n")
        new_lines.append("  initialValues?: Partial<PersonFormValues>;\n")
        new_lines.append("  onSubmit: (data: any) => Promise<unknown>;\n")
        new_lines.append("  onCancel?: () => void;\n")
        new_lines.append("  submitLabel?: string;\n")
        new_lines.append("  isCreate?: boolean;\n")
        new_lines.append("  preselectedFamilyId?: string;\n")
        new_lines.append("  currentPersonId?: string;\n")
        new_lines.append("}\n")
    if line.startswith("export function PersonForm({"):
        skip = False
    
    if not skip:
        new_lines.append(line)

with open("frontend/src/components/people/PersonForm.tsx", "w") as f:
    f.writelines(new_lines)
