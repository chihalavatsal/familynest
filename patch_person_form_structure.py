import re

with open("frontend/src/components/people/PersonForm.tsx", "r") as f:
    content = f.read()

# Add imports for ModalBody and ModalFooter
if "ModalBody" not in content:
    content = content.replace("import { Button }", "import { ModalBody, ModalFooter } from '../ui/Dialog';\nimport { Button }")

# Update renderWizard
old_wizard_start = """  const renderWizard = () => {
    return (
      <div className="fn-fade-in">"""

new_wizard_start = """  const renderWizard = () => {
    return (
      <div className="flex flex-col flex-1 min-h-0 fn-fade-in">
        <ModalBody>"""
content = content.replace(old_wizard_start, new_wizard_start)

old_wizard_end = """        <div className="flex gap-3 pt-6 mt-6 justify-between border-t border-stone-100">
          <div>
            {step > 1 ? (
              <Button type="button" variant="secondary" onClick={() => setStep(s => s - 1)}>
                Back
              </Button>
            ) : onCancel ? (
              <Button type="button" variant="secondary" onClick={onCancel}>
                Cancel
              </Button>
            ) : <div/>}
          </div>
          <div>
            {step < 4 ? (
              <Button type="button" variant="primary" onClick={() => {
                if (step === 1 && !values.first_name.trim()) {
                  setErrors({first_name: 'First name is required'});
                  return;
                }
                setStep(s => s + 1);
              }}>
                Continue
              </Button>
            ) : (
              <Button type="submit" variant="primary" loading={loading}>
                {loading ? 'Adding...' : submitLabel}
              </Button>
            )}
          </div>
        </div>
      </div>
    );
  };"""

new_wizard_end = """        </ModalBody>
        <ModalFooter>
          <div className="flex w-full justify-between">
            <div>
              {step > 1 ? (
                <Button type="button" variant="secondary" onClick={() => setStep(s => s - 1)}>
                  Back
                </Button>
              ) : onCancel ? (
                <Button type="button" variant="secondary" onClick={onCancel}>
                  Cancel
                </Button>
              ) : <div/>}
            </div>
            <div>
              {step < 4 ? (
                <Button type="button" variant="primary" onClick={() => {
                  if (step === 1 && !values.first_name.trim()) {
                    setErrors({first_name: 'First name is required'});
                    return;
                  }
                  setStep(s => s + 1);
                }}>
                  Continue
                </Button>
              ) : (
                <Button type="submit" variant="primary" loading={loading}>
                  {loading ? 'Adding...' : submitLabel}
                </Button>
              )}
            </div>
          </div>
        </ModalFooter>
      </div>
    );
  };"""
content = content.replace(old_wizard_end, new_wizard_end)

# Update renderEdit
old_edit_start = """  const renderEdit = () => {
    return (
      <div className="fn-fade-in">
        {apiError && <InlineError message={apiError} />}"""

new_edit_start = """  const renderEdit = () => {
    return (
      <div className="flex flex-col flex-1 min-h-0 fn-fade-in">
        <ModalBody>
          {apiError && <InlineError message={apiError} />}"""
content = content.replace(old_edit_start, new_edit_start)

old_edit_end = """        </section>

        <div className="flex gap-3 pt-4 mt-6 justify-end border-t border-stone-100 sticky bottom-0 bg-white/95 backdrop-blur py-4 -mb-4">
          {onCancel && (
            <Button type="button" variant="secondary" size="md" onClick={onCancel} disabled={loading}>
              Cancel
            </Button>
          )}
          <Button type="submit" variant="primary" size="md" loading={loading}>
            {loading ? 'Saving...' : submitLabel}
          </Button>
        </div>
      </div>
    );
  };"""

new_edit_end = """        </section>
        </ModalBody>
        <ModalFooter>
          {onCancel && (
            <Button type="button" variant="secondary" size="md" onClick={onCancel} disabled={loading}>
              Cancel
            </Button>
          )}
          <Button type="submit" variant="primary" size="md" loading={loading}>
            {loading ? 'Saving...' : submitLabel}
          </Button>
        </ModalFooter>
      </div>
    );
  };"""
content = content.replace(old_edit_end, new_edit_end)

# Update the form wrapper
old_return = """  return (
    <form onSubmit={handleSubmit} noValidate>
      {isCreate ? renderWizard() : renderEdit()}
    </form>
  );"""

new_return = """  return (
    <form onSubmit={handleSubmit} noValidate className="flex flex-col flex-1 min-h-0">
      {isCreate ? renderWizard() : renderEdit()}
    </form>
  );"""
content = content.replace(old_return, new_return)

with open("frontend/src/components/people/PersonForm.tsx", "w") as f:
    f.write(content)

