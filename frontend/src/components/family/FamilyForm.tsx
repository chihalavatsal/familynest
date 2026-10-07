import { useState } from 'react';
import { Input } from '../ui/Input';
import { Textarea } from '../ui/FormFields';
import { Button } from '../ui/Button';
import { InlineError } from '../feedback';
import { ModalBody, ModalFooter } from '../ui/Dialog';
import type { FamilyCreatePayload } from '../../types';

interface FamilyFormProps {
  initialValues?: { name: string; description?: string | null };
  onSubmit: (data: FamilyCreatePayload) => Promise<unknown>;
  onCancel?: () => void;
  submitLabel?: string;
  isCreate?: boolean;
}

export function FamilyForm({
  initialValues,
  onSubmit,
  onCancel,
  submitLabel = 'Save',
  isCreate = false,
}: FamilyFormProps) {
  const [name, setName] = useState(initialValues?.name ?? '');
  const [description, setDescription] = useState(initialValues?.description ?? '');
  const [errors, setErrors] = useState<{ name?: string }>({});
  const [apiError, setApiError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const validate = (): boolean => {
    const errs: typeof errors = {};
    if (!name.trim()) errs.name = 'Family name is required';
    else if (name.trim().length > 255) errs.name = 'Name must be 255 characters or fewer';
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setApiError(null);
    if (!validate()) return;
    setLoading(true);
    try {
      await onSubmit({
        name: name.trim(),
        description: description.trim() || undefined,
      });
    } catch (err: unknown) {
      const apiErr = err as { message?: string };
      setApiError(apiErr.message ?? 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} noValidate className="flex flex-col flex-1 min-h-0 overflow-hidden">
      <ModalBody>
        <div className="space-y-4">
          {isCreate && (
            <p className="text-[14px] text-stone-500 leading-relaxed mb-4">
              Keep one branch of your family organized without merging it with other family networks.
            </p>
          )}

          {apiError && <InlineError message={apiError} />}

          <Input
            label="Family name"
            value={name}
            onChange={(e) => {
              setName(e.target.value);
              setErrors((prev) => ({ ...prev, name: undefined }));
            }}
            error={errors.name}
            required
            placeholder="e.g. Patel Family"
            autoFocus={isCreate}
          />

          <Textarea
            label="Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Optional description of this family space…"
            rows={3}
            hint="Helps clarify which branch this family space represents."
          />
        </div>
      </ModalBody>
      
      <ModalFooter>
        {onCancel && (
          <Button type="button" variant="secondary" onClick={onCancel} disabled={loading} className="w-full sm:w-auto">
            Cancel
          </Button>
        )}
        <Button type="submit" loading={loading} className="w-full sm:w-auto">
          {loading && isCreate ? 'Creating...' : loading ? 'Saving...' : submitLabel}
        </Button>
      </ModalFooter>
    </form>
  );
}
