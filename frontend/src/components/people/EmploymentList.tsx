import React, { useEffect, useState } from 'react';
import { api } from '../../api/client';
import { Briefcase, Plus, Trash2, Building, MapPin, Tag } from 'lucide-react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Select, Textarea } from '../ui/FormFields';
import { Modal, ModalBody, ModalFooter } from '../ui/Dialog';

export function EmploymentList({ personId, canEdit }: { personId: string, canEdit: boolean }) {
  const [employments, setEmployments] = useState<any[]>([]);
  const [showAdd, setShowAdd] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const [employer, setEmployer] = useState('');
  const [title, setTitle] = useState('');
  const [department, setDepartment] = useState('');
  const [location, setLocation] = useState('');
  const [employmentType, setEmploymentType] = useState('');
  const [description, setDescription] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [isCurrent, setIsCurrent] = useState(true);

  useEffect(() => {
    load();
  }, [personId]);

  const load = async () => {
    const res = await api.get(`/people/${personId}/employments`);
    setEmployments(res as any[]);
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isSubmitting) return;
    setIsSubmitting(true);
    try {
    await api.post(`/people/${personId}/employments`, {
      employer_name: employer,
      job_title: title,
      department: department || undefined,
      location: location || undefined,
      employment_type: employmentType || undefined,
      description: description || undefined,
      start_date: startDate || undefined,
      end_date: endDate || undefined,
      is_current: isCurrent
    });
    setShowAdd(false);
      resetForm();
      load();
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setEmployer('');
    setTitle('');
    setDepartment('');
    setLocation('');
    setEmploymentType('');
    setDescription('');
    setStartDate('');
    setEndDate('');
    setIsCurrent(true);
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this employment record?')) return;
    if (isSubmitting) return;
    setIsSubmitting(true);
    try {
    await api.delete(`/people/${personId}/employments/${id}`);
      await load();
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatEmploymentType = (type?: string) => {
    if (!type) return null;
    return type.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  };

  return (
    <div className="mt-8">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-[13px] font-semibold text-stone-900 uppercase tracking-wider flex items-center gap-2">
          <Briefcase className="w-4 h-4" /> Work History
        </h3>
        {canEdit && (
          <button onClick={() => setShowAdd(true)} className="text-[#92614a] text-sm font-medium flex items-center gap-1 hover:underline">
            <Plus className="w-4 h-4" /> Add
          </button>
        )}
      </div>

      <div className="space-y-4">
        {employments.length === 0 ? (
          <p className="text-sm text-stone-500 italic">No work history provided.</p>
        ) : (
          employments.map(emp => (
            <div key={emp.id} className="bg-stone-50 p-4 rounded-xl border border-stone-100 flex justify-between items-start">
              <div className="flex-1">
                <div className="font-semibold text-stone-900">{emp.job_title}</div>
                
                <div className="text-sm text-stone-700 font-medium mt-0.5">{emp.employer_name}</div>
                
                <div className="flex flex-wrap gap-x-4 gap-y-1 mt-2 text-[13px] text-stone-500">
                  {emp.department && (
                    <span className="flex items-center gap-1"><Building className="w-3.5 h-3.5" /> {emp.department}</span>
                  )}
                  {emp.location && (
                    <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5" /> {emp.location}</span>
                  )}
                  {emp.employment_type && (
                    <span className="flex items-center gap-1"><Tag className="w-3.5 h-3.5" /> {formatEmploymentType(emp.employment_type)}</span>
                  )}
                </div>

                <div className="text-[12px] text-stone-500 mt-2 font-medium">
                  {emp.start_date ? new Date(emp.start_date).toLocaleDateString(undefined, { year: 'numeric', month: 'short' }) : 'Unknown start'} 
                  {' — '} 
                  {emp.is_current ? 'Present' : (emp.end_date ? new Date(emp.end_date).toLocaleDateString(undefined, { year: 'numeric', month: 'short' }) : 'Unknown end')}
                </div>
                
                {emp.description && (
                  <p className="text-[13px] text-stone-600 mt-3 whitespace-pre-wrap">{emp.description}</p>
                )}
              </div>
              
              {canEdit && (
                <button onClick={() => handleDelete(emp.id)} className="text-stone-400 hover:text-red-500 transition-colors ml-4 p-1">
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
            </div>
          ))
        )}
      </div>

      <Modal isOpen={showAdd} onClose={() => { setShowAdd(false); resetForm(); }} title="Add Employment" size="lg">
        <form onSubmit={handleAdd} className="flex flex-col flex-1 min-h-0 overflow-hidden">
          <ModalBody>
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Input label="Employer / Company *" value={employer} onChange={e => setEmployer(e.target.value)} required />
                <Input label="Job Title *" value={title} onChange={e => setTitle(e.target.value)} required />
              </div>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Input label="Department" value={department} onChange={e => setDepartment(e.target.value)} placeholder="e.g. Engineering, Sales" />
                <Input label="Location" value={location} onChange={e => setLocation(e.target.value)} placeholder="e.g. San Francisco, CA" />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Select label="Employment Type" value={employmentType} onChange={e => setEmploymentType(e.target.value)}>
                  <option value="">-- Select --</option>
                  <option value="full_time">Full-time</option>
                  <option value="part_time">Part-time</option>
                  <option value="contract">Contract</option>
                  <option value="freelance">Freelance</option>
                  <option value="intern">Internship</option>
                </Select>
                <div></div>
              </div>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Input label="Start Date" type="date" value={startDate} onChange={e => setStartDate(e.target.value)} />
                <Input label="End Date" type="date" value={endDate} onChange={e => setEndDate(e.target.value)} disabled={isCurrent} />
              </div>
              
              <label className="flex items-center gap-2 cursor-pointer select-none">
                <input type="checkbox" checked={isCurrent} onChange={e => { setIsCurrent(e.target.checked); if (e.target.checked) setEndDate(''); }} className="w-4 h-4 rounded border-stone-300 text-[#92614a] focus:ring-[#92614a]/40" />
                <span className="text-sm text-stone-700 font-medium">I currently work here</span>
              </label>

              <Textarea 
                label="Description" 
                value={description} 
                onChange={e => setDescription(e.target.value)} 
                rows={4}
                placeholder="Describe your role, responsibilities, and achievements..."
              />
            </div>
          </ModalBody>
          <ModalFooter>
            <Button type="button" variant="secondary" onClick={() => { setShowAdd(false); resetForm(); }}>Cancel</Button>
            <Button type="submit" variant="primary" loading={isSubmitting} disabled={!employer || !title || isSubmitting}>Save</Button>
          </ModalFooter>
        </form>
      </Modal>
    </div>
  );
}
