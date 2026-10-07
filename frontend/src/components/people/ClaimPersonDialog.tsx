import { useState } from 'react';
import { UserCheck } from 'lucide-react';
import { peopleApi } from '../../api/people';
import type { PersonDetailResponse, ApiError } from '../../types';
import { Modal, ModalHeader } from "../ui/Dialog";
import { Button } from '../ui/Button';
import { InlineError } from '../feedback';

interface ClaimPersonDialogProps {
  person: PersonDetailResponse;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function ClaimPersonDialog({
  person,
  isOpen,
  onClose,
  onSuccess,
}: ClaimPersonDialogProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fullName = [person.first_name, person.last_name].filter(Boolean).join(' ');

  const handleClaim = async () => {
    setError(null);
    setLoading(true);
    try {
      await peopleApi.claim(person.id);
      onSuccess();
      onClose();
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      setError(apiErr.message ?? 'Could not connect this profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen}  onClose={onClose} size="sm">
      <ModalHeader title="Connect profile to your account" onClose={onClose} />
      <div className="space-y-5">
        <div className="flex items-start gap-3 p-4 rounded-xl bg-[#fdf4ed] border border-[#e8d9cc]">
          <UserCheck className="w-5 h-5 text-[#92614a] mt-0.5 shrink-0" />
          <div>
            <p className="text-[14px] font-medium text-[#7d5240] mb-1">
              Connect "{fullName}" to your account
            </p>
            <p className="text-[13px] text-stone-600 leading-relaxed">
              This will link this existing family profile to your FamilyNest account. You will not create a duplicate person.
            </p>
          </div>
        </div>

        {error && <InlineError message={error} />}

        <div className="text-[13px] text-stone-500 space-y-1">
          <p>By connecting this profile:</p>
          <ul className="list-disc list-inside space-y-0.5 ml-2 text-[12px]">
            <li>You become the account owner of this person record</li>
            <li>No duplicate person will be created</li>
            <li>Your existing family memberships remain unchanged</li>
          </ul>
        </div>

        <div className="flex gap-3 justify-end pt-2 border-t border-stone-100">
          <Button variant="secondary" size="sm" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button
            variant="primary"
            size="sm"
            loading={loading}
            onClick={handleClaim}
            leftIcon={<UserCheck className="w-4 h-4" />}
          >
            Connect profile
          </Button>
        </div>
      </div>
    </Modal>
  );
}
