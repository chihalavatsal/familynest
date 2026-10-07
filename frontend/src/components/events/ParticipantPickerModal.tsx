import { MemberPicker } from '../family/MemberPicker';
import { eventsApi } from '../../api/events';
import { useToast } from '../ui/Toast';
import type { EventParticipantResponse } from '../../types';

interface ParticipantPickerModalProps {
  eventId: string;
  existingParticipantIds: string[];
  isOpen: boolean;
  onClose: () => void;
  onAdded: (participant: EventParticipantResponse) => void;
}

export function ParticipantPickerModal({ eventId, existingParticipantIds, isOpen, onClose, onAdded }: ParticipantPickerModalProps) {
  const { success, error } = useToast();

  const handleSelect = async (person: any) => {
    if (existingParticipantIds.includes(person.id)) {
      error('Person is already a participant.');
      return;
    }
    
    try {
      const res = await eventsApi.addParticipant(eventId, person.id);
      success('Participant added.');
      onAdded(res);
      onClose();
    } catch (err: any) {
      error(err.message ?? 'Could not add participant.');
    }
  };

  return (
    <MemberPicker
      isOpen={isOpen}
      title="Add Participant"
      excludePersonIds={existingParticipantIds}
      onSelect={handleSelect}
      onClose={onClose}
    />
  );
}
