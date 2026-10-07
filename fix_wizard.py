import re

with open('frontend/src/components/people/AddRelativeWizard.tsx', 'r') as f:
    content = f.read()

# Replace step initialization
content = content.replace("const [step, setStep] = useState(1);", "const [step, setStep] = useState(currentPersonId ? 1 : 2);")

# Replace getStepNumber
old_getStepNumber = """  const getStepNumber = () => {
    if (step === 1) return 1;
    if (step === 1.5) return 2;
    if (step === 2) return needsSideSelection(relativeType as RelativeType) ? 3 : 2;
    if (step === 3) return totalSteps;
    return step;
  };"""
new_getStepNumber = """  const getStepNumber = () => {
    if (!currentPersonId) {
      if (step === 2) return 1;
      if (step === 3) return 2;
    }
    if (step === 1) return 1;
    if (step === 1.5) return 2;
    if (step === 2) return needsSideSelection(relativeType as RelativeType) ? 3 : 2;
    if (step === 3) return totalSteps;
    return step;
  };"""
content = content.replace(old_getStepNumber, new_getStepNumber)

# Replace totalSteps calculation
old_getTotalSteps = """  const getTotalSteps = () => {
    if (needsSideSelection(relativeType as RelativeType)) return 4;
    return 3;
  };"""
new_getTotalSteps = """  const getTotalSteps = () => {
    if (!currentPersonId) return 2;
    if (needsSideSelection(relativeType as RelativeType)) return 4;
    return 3;
  };"""
content = content.replace(old_getTotalSteps, new_getTotalSteps)

# Hide Back button on step 2 if !currentPersonId
content = content.replace("""{step > 1 && (
              <Button type="button" variant="secondary" onClick={() => setStep(step === 2 && needsSideSelection(relativeType as RelativeType) ? 1.5 : step - 1)}>
                Back
              </Button>
            )}""", """{step > (currentPersonId ? 1 : 2) && (
              <Button type="button" variant="secondary" onClick={() => setStep(step === 2 && needsSideSelection(relativeType as RelativeType) ? 1.5 : step - 1)}>
                Back
              </Button>
            )}""")

with open('frontend/src/components/people/AddRelativeWizard.tsx', 'w') as f:
    f.write(content)
print("Done")
