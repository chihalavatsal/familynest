with open("frontend/src/pages/Memories/MemoryCreatePage.tsx", "r") as f:
    content = f.read()

import re

new_content = """import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { memoriesApi } from '../../api/memories';

import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Select, Textarea } from '../../components/ui/FormFields';
import { useToast } from '../../components/ui/Toast';

export function MemoryCreatePage() {
  const [currentFamilyId, setCurrentFamilyId] = useState<string | null>(null);
  
  useEffect(() => {
    fetch('/api/v1/families', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
      .then(r => r.json())
      .then(d => {
        if (d.items && d.items.length > 0) setCurrentFamilyId(d.items[0].id);
      })
      .catch(console.error);
  }, []);
  const navigate = useNavigate();
  const { success, error: toastError } = useToast();
  
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [memoryDate, setMemoryDate] = useState('');
  const [visibility, setVisibility] = useState('family');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentFamilyId || !title.trim() || !body.trim()) return;
    
    try {
      setIsSubmitting(true);
      const res = await memoriesApi.create({
        family_id: currentFamilyId,
        title: title.trim(),
        body: body.trim(),
        memory_date: memoryDate || undefined,
        visibility: visibility
      });
      success('Memory created successfully');
      navigate(`/memories/${res.id}`);
    } catch (err: any) {
      toastError(err.message || 'Failed to create memory');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-[760px] mx-auto py-8 px-4 sm:px-6">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-serif text-stone-900 font-semibold mb-1">Create Memory</h1>
          <p className="text-sm text-stone-500">Record a family story or memory to share with the network.</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col space-y-8 bg-white p-6 sm:p-8 rounded-2xl border border-stone-100 shadow-sm">
        <section>
          <h3 className="text-sm font-semibold text-stone-900 mb-4 uppercase tracking-wider">1. Memory Details</h3>
          <div className="space-y-4">
            <Input
              label="Title *"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g., Grandfather's 70th Birthday"
            />
            <Textarea
              label="Story *"
              required
              rows={8}
              value={body}
              onChange={(e) => setBody(e.target.value)}
              placeholder="Write the story here..."
            />
            <Input
              label="Date (Optional)"
              type="date"
              value={memoryDate}
              onChange={(e) => setMemoryDate(e.target.value)}
            />
          </div>
        </section>

        <section>
          <h3 className="text-sm font-semibold text-stone-900 mb-4 uppercase tracking-wider">2. Visibility</h3>
          <div className="space-y-4">
            <Select
              label="Audience"
              value={visibility}
              onChange={(e) => setVisibility(e.target.value)}
            >
              <option value="family">Family (Everyone in the space)</option>
              <option value="selected_members">Selected Members Only</option>
            </Select>
          </div>
        </section>

        <div className="flex justify-end gap-3 pt-6 border-t border-stone-100">
          <Button variant="ghost" type="button" onClick={() => navigate('/memories')} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" loading={isSubmitting} disabled={!title.trim() || !body.trim()}>
            {isSubmitting ? 'Saving...' : 'Save Memory'}
          </Button>
        </div>
      </form>
    </div>
  );
}
"""

with open("frontend/src/pages/Memories/MemoryCreatePage.tsx", "w") as f:
    f.write(new_content)
