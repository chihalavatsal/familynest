import { useEffect, useState } from 'react';
import { Users } from 'lucide-react';
import { graphApi } from '../../api/graph';
import type { RelatedPersonItem, ApiError } from '../../types';
import { Modal, ModalHeader, ModalBody } from "../ui/Dialog";
import { PersonCard } from '../people/PersonCard';
import { ListSkeleton, ErrorState, EmptyState } from '../feedback';

interface RelatedListModalProps {
  isOpen: boolean;
  type: 'ancestors' | 'descendants' | 'siblings';
  personId: string;
  personName: string;
  onSelect: (personId: string) => void;
  onClose: () => void;
}

export function RelatedListModal({ isOpen, type, personId, personName, onSelect, onClose }: RelatedListModalProps) {
  const [items, setItems] = useState<RelatedPersonItem[]>([]);
  const [loadState, setLoadState] = useState<'loading' | 'error' | 'ready'>('loading');
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    if (!isOpen) return;
    let mounted = true;
    setLoadState('loading');
    
    const fetcher = 
      type === 'ancestors' ? graphApi.getAncestors(personId) :
      type === 'descendants' ? graphApi.getDescendants(personId) :
      graphApi.getSiblings(personId);

    fetcher
      .then(res => {
        if (mounted) {
          // If ancestors, reverse to show oldest first ("up to down")
          const itemsToSet = type === 'ancestors' ? [...res.items].reverse() : res.items;
          setItems(itemsToSet);
          setLoadState('ready');
        }
      })
      .catch(err => {
        if (mounted) {
          const apiErr = err as ApiError;
          setErrorMsg(apiErr.message ?? 'Could not load relationships.');
          setLoadState('error');
        }
      });
      
    return () => { mounted = false; };
  }, [isOpen, type, personId]);

  const title = type.charAt(0).toUpperCase() + type.slice(1);

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="sm"
      fullHeight>
      <ModalHeader title={`${title} for ${personName}`} onClose={onClose} />
      <ModalBody>
        {loadState === 'loading' && <ListSkeleton rows={4} />}
        
        {loadState === 'error' && (
          <ErrorState message={errorMsg} />
        )}

        {loadState === 'ready' && items.length === 0 && (
          <EmptyState
            icon={<Users className="w-5 h-5" />}
            title={`No ${type} found`}
            description={`There are no known ${type} in the family graph.`}
          />
        )}

        {loadState === 'ready' && items.length > 0 && (
          <ul role="list" className="divide-y divide-stone-50 -mx-5 sm:-mx-8">
            {items.map(item => (
              <li key={item.person.id}>
                <PersonCard
                  person={{
                    ...item.person,
                    is_deceased: item.person.is_deceased ?? false,
                    is_minor: item.person.is_minor ?? false,
                    profile_status: item.person.profile_status ?? 'unclaimed',
                    created_at: '',
                    updated_at: ''
                  } as any}
                  compact
                  onClick={() => onSelect(item.person.id)}
                  action={
                    <span className="text-[12px] text-stone-400 capitalize">{item.relationship?.replace(/_/g, ' ')}</span>
                  }
                />
              </li>
            ))}
          </ul>
        )}
      </ModalBody>
    </Modal>
  );
}
