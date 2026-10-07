import { eventsApi } from '../../api/events';
import { useToast } from '../ui/Toast';
import { Modal, ModalHeader } from "../ui/Dialog";
import { EventForm } from './EventForm';
import type { EventCreatePayload } from '../../types';

interface CreateEventModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreated: () => void;
}

export function CreateEventModal({ isOpen, onClose, onCreated }: CreateEventModalProps) {
  const { success: successToast } = useToast();

  const handleSubmit = async (payload: EventCreatePayload) => {
    await eventsApi.create(payload);
    successToast('Event created successfully.');
    onCreated();
    onClose();
  };

  return (
    <Modal isOpen={isOpen}  onClose={onClose} size="md"
        fullHeight>
      <ModalHeader title="Create Event" onClose={onClose} />
      <EventForm
        submitLabel="Create Event"
        onSubmit={handleSubmit}
        onCancel={onClose}
      />
    </Modal>
  );
}
