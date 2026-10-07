import React, { useEffect, useState } from 'react';
import { api } from '../../api/client';
import { GraduationCap, Plus, Trash2 } from 'lucide-react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Modal } from '../ui/Dialog';

export function EducationList({ personId, canEdit }: { personId: string, canEdit: boolean }) {
  const [educations, setEducations] = useState<any[]>([]);
  const [showAdd, setShowAdd] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [institution, setInstitution] = useState('');
  const [degree, setDegree] = useState('');
  const [fieldOfStudy, setFieldOfStudy] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  useEffect(() => {
    load();
  }, [personId]);

  const load = async () => {
    const res = await api.get(`/people/${personId}/educations`);
    setEducations(res as any[]);
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isSubmitting) return;
    setIsSubmitting(true);
    try {
    await api.post(`/people/${personId}/educations`, {
      institution,
      degree: degree || undefined,
      field_of_study: fieldOfStudy || undefined,
      start_date: startDate || undefined,
      end_date: endDate || undefined
    });
    setShowAdd(false);
    setInstitution('');
    setDegree('');
    setFieldOfStudy('');
    setStartDate('');
    setEndDate('');
      load();
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this education record?')) return;
    if (isSubmitting) return;
    setIsSubmitting(true);
    try {
    await api.delete(`/people/${personId}/educations/${id}`);
      await load();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mt-8">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-[13px] font-semibold text-stone-900 uppercase tracking-wider flex items-center gap-2">
          <GraduationCap className="w-4 h-4" /> Education
        </h3>
        {canEdit && (
          <button onClick={() => setShowAdd(true)} className="text-[#92614a] text-sm font-medium flex items-center gap-1 hover:underline">
            <Plus className="w-4 h-4" /> Add
          </button>
        )}
      </div>

      <div className="space-y-4">
        {educations.length === 0 ? (
          <p className="text-sm text-stone-500 italic">No education history provided.</p>
        ) : (
          educations.map(edu => (
            <div key={edu.id} className="bg-stone-50 p-4 rounded-lg flex justify-between items-start">
              <div>
                <div className="font-medium text-stone-900">{edu.institution}</div>
                {(edu.degree || edu.field_of_study) && (
                  <div className="text-sm text-stone-600">
                    {edu.degree}{edu.degree && edu.field_of_study ? ' in ' : ''}{edu.field_of_study}
                  </div>
                )}
                <div className="text-[13px] text-stone-500 mt-1">
                  {edu.start_date ? new Date(edu.start_date).getFullYear() : 'Unknown start'} — {edu.end_date ? new Date(edu.end_date).getFullYear() : 'Unknown end'}
                </div>
              </div>
              {canEdit && (
                <button onClick={() => handleDelete(edu.id)} className="text-stone-400 hover:text-red-500 transition-colors">
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
            </div>
          ))
        )}
      </div>

      <Modal isOpen={showAdd} onClose={() => setShowAdd(false)} title="Add Education" size="md">
        <form onSubmit={handleAdd} className="space-y-4">
          <Input label="Institution" value={institution} onChange={e => setInstitution(e.target.value)} required />
          <div className="grid grid-cols-2 gap-3">
            <Input label="Degree (e.g. BTech)" value={degree} onChange={e => setDegree(e.target.value)} />
            <Input label="Field of Study" value={fieldOfStudy} onChange={e => setFieldOfStudy(e.target.value)} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Input label="Start Date" type="date" value={startDate} onChange={e => setStartDate(e.target.value)} />
            <Input label="End Date" type="date" value={endDate} onChange={e => setEndDate(e.target.value)} />
          </div>
          <div className="pt-4 flex justify-end gap-3">
            <Button type="button" variant="secondary" onClick={() => setShowAdd(false)}>Cancel</Button>
            <Button type="submit" variant="primary" loading={isSubmitting} disabled={!institution || isSubmitting}>Save</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
