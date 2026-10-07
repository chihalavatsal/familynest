import { useState, useEffect } from 'react';
import { notificationsApi } from '../../api/notifications';
import { Button } from '../ui/Button';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../ui/Dialog';

export function NotificationSettingsModal({ isOpen, onClose }: { isOpen: boolean, onClose: () => void }) {
  const [preferences, setPreferences] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      notificationsApi.getPreferences()
        .then(res => setPreferences(res))
        .finally(() => setLoading(false));
    }
  }, [isOpen]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!preferences) return;
    setSaving(true);
    try {
      await notificationsApi.updatePreferences(preferences);
      onClose();
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const toggle = (field: string) => {
    setPreferences((prev: any) => ({ ...prev, [field]: !prev[field] }));
  };

  if (loading) {
    return (
      <Modal isOpen={isOpen} onClose={onClose} size="md"
      fullHeight>
        <ModalHeader title="Notification Settings" onClose={onClose} />
        <ModalBody>
          <div className="p-6 text-center text-stone-500">Loading settings...</div>
        </ModalBody>
      </Modal>
    );
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="md"
      fullHeight>
      <ModalHeader title="Notification Settings" onClose={onClose} />
      <form onSubmit={handleSave} className="flex flex-col flex-1 min-h-0 overflow-hidden">
        <ModalBody>
          <div className="space-y-6">
            <h3 className="text-[14px] font-semibold text-stone-900 border-b border-stone-100 pb-2">Delivery</h3>
            
            <label className="flex items-start justify-between gap-4 cursor-pointer">
              <div>
                <div className="text-[14px] font-medium text-stone-900">In-App Notifications</div>
                <div className="text-[13px] text-stone-500">Receive notifications within FamilyNest</div>
              </div>
              <input 
                type="checkbox" 
                checked={preferences?.in_app_enabled ?? true} 
                onChange={() => toggle('in_app_enabled')}
                className="w-4 h-4 mt-1 rounded border-stone-300 text-[#92614a] focus:ring-[#92614a]"
              />
            </label>

            <h3 className="text-[14px] font-semibold text-stone-900 border-b border-stone-100 pb-2 pt-2">Life Events</h3>

            <label className="flex items-start justify-between gap-4 cursor-pointer">
              <div>
                <div className="text-[14px] font-medium text-stone-900">Birthdays</div>
                <div className="text-[13px] text-stone-500">Get reminded of family birthdays</div>
              </div>
              <input 
                type="checkbox" 
                checked={preferences?.birthdays_enabled ?? true} 
                onChange={() => toggle('birthdays_enabled')}
                className="w-4 h-4 mt-1 rounded border-stone-300 text-[#92614a] focus:ring-[#92614a]"
              />
            </label>

            <label className="flex items-start justify-between gap-4 cursor-pointer">
              <div>
                <div className="text-[14px] font-medium text-stone-900">Anniversaries</div>
                <div className="text-[13px] text-stone-500">Get reminded of wedding anniversaries</div>
              </div>
              <input 
                type="checkbox" 
                checked={preferences?.anniversaries_enabled ?? true} 
                onChange={() => toggle('anniversaries_enabled')}
                className="w-4 h-4 mt-1 rounded border-stone-300 text-[#92614a] focus:ring-[#92614a]"
              />
            </label>

            <label className="flex items-start justify-between gap-4 cursor-pointer">
              <div>
                <div className="text-[14px] font-medium text-stone-900">Remembrances</div>
                <div className="text-[13px] text-stone-500">Remember loved ones on the anniversary of their passing</div>
              </div>
              <input 
                type="checkbox" 
                checked={preferences?.remembrance_enabled ?? true} 
                onChange={() => toggle('remembrance_enabled')}
                className="w-4 h-4 mt-1 rounded border-stone-300 text-[#92614a] focus:ring-[#92614a]"
              />
            </label>

            <label className="flex items-start justify-between gap-4 cursor-pointer">
              <div>
                <div className="text-[14px] font-medium text-stone-900">Work Anniversaries</div>
                <div className="text-[13px] text-stone-500">Celebrate professional milestones</div>
              </div>
              <input 
                type="checkbox" 
                checked={preferences?.work_anniversaries_enabled ?? true} 
                onChange={() => toggle('work_anniversaries_enabled')}
                className="w-4 h-4 mt-1 rounded border-stone-300 text-[#92614a] focus:ring-[#92614a]"
              />
            </label>

          </div>
        </ModalBody>
        <ModalFooter>
          <div className="flex w-full justify-between">
            <Button type="button" variant="secondary" onClick={onClose}>Cancel</Button>
            <Button type="submit" variant="primary" loading={saving}>Save Settings</Button>
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}
