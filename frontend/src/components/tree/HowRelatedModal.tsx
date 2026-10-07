import { useState } from 'react';
import { Route } from 'lucide-react';
import { graphApi } from '../../api/graph';
import type { KinshipResult, ApiError } from '../../types';
import { Modal, ModalHeader, ModalBody } from "../ui/Dialog";
import { Button } from '../ui/Button';
import { EmptyState, ErrorState, ListSkeleton } from '../feedback';
import { MemberPicker } from '../family/MemberPicker';
import { Avatar, Badge } from '../ui/Primitives';

interface HowRelatedModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function HowRelatedModal({ isOpen, onClose }: HowRelatedModalProps) {
  const [targetId, setTargetId] = useState<string | null>(null);
  const [showPicker, setShowPicker] = useState(false);
  const [result, setResult] = useState<KinshipResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const calculate = async (id: string) => {
    setLoading(true);
    setErrorMsg(null);
    setResult(null);
    try {
      // The API is technically centered around current user but if we want arbitrary two people, 
      // the backend endpoints provided were `how-related/{person_id}` which uses current_user.
      // Wait, if the prompt said:
      // You
      //  ↓ parent
      // Your mother
      //
      // The endpoint is `get_kinship(user_id=current_user.id, target_id=person_id)`
      // This means the API only computes relationship from the CURRENT USER to someone else.
      // We don't have a source_id AND target_id parameter.
      // So the HowRelatedModal actually calculates how the CURRENT USER is related to the selected person!
      // Let's modify this to reflect that.
      
      const res = await graphApi.howRelated(id);
      setResult(res);
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      setErrorMsg(apiErr.message ?? 'Could not calculate relationship.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectTarget = (id: string) => {
    setTargetId(id);
    setShowPicker(false);
    calculate(id);
  };

  return (
    <Modal isOpen={isOpen}  onClose={onClose} size="md"
      fullHeight>
      <ModalHeader title="How am I related?" onClose={onClose} />
      <ModalBody>
      <div className="space-y-6">
        
        <div className="flex flex-col items-center justify-center py-4">
          <Button variant="secondary" onClick={() => setShowPicker(true)}>
            {targetId ? 'Change person' : 'Select a person'}
          </Button>
        </div>

        {showPicker && (
          <MemberPicker
            isOpen={showPicker}
            title="Calculate relationship to..."
            onSelect={(p) => handleSelectTarget(p.id)}
            onClose={() => setShowPicker(false)}
          />
        )}

        {loading && <ListSkeleton rows={3} />}

        {errorMsg && <ErrorState message={errorMsg} onRetry={() => targetId && calculate(targetId)} />}

        {result && (
          <div className="bg-stone-50 rounded-xl p-5 border border-stone-100">
            <h3 className="text-[15px] font-semibold text-stone-900 mb-4 text-center">
              You are: <span className="text-[#92614a] capitalize">{result.relationship?.replace(/_/g, ' ') || 'Connected'}</span>
            </h3>

            {result.path.length === 0 ? (
              <EmptyState
                icon={<Route className="w-5 h-5" />}
                title="No relationship path found"
                description="These two people are currently not connected through the available family relationship graph."
              />
            ) : (
              <div className="relative pl-6 space-y-6 before:absolute before:inset-y-2 before:left-[11px] before:w-px before:bg-stone-200">
                
                {/* Source Person (You) */}
                <div className="relative">
                  <div className="absolute -left-[30px] top-1.5 w-2 h-2 rounded-full bg-[#92614a] ring-4 ring-stone-50" />
                  <div className="flex items-center gap-3">
                    <Avatar name={result.source_person.first_name} photoUrl={result.source_person.profile_photo_url} size="sm" />
                    <div>
                      <p className="text-[14px] font-medium text-stone-900">{result.source_person.first_name}</p>
                      <Badge variant="primary" className="text-[10px] mt-0.5">You</Badge>
                    </div>
                  </div>
                </div>

                {/* Path Nodes */}
                {result.path.map((node, i) => (
                  <div key={i} className="relative">
                    {/* Relationship Arrow Label */}
                    <div className="absolute -left-[28px] -top-5 text-[10px] text-stone-400 uppercase tracking-wider bg-stone-50 py-1">
                      ↓ {node.relationship.replace(/_/g, ' ')}
                    </div>
                    
                    <div className="absolute -left-[30px] top-1.5 w-2 h-2 rounded-full bg-stone-300 ring-4 ring-stone-50" />
                    <div className="flex items-center gap-3">
                      <Avatar name={node.person.first_name} photoUrl={node.person.profile_photo_url} size="sm" />
                      <div>
                        <p className="text-[14px] font-medium text-stone-900">{node.person.first_name}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
      </ModalBody>
    </Modal>
  );
}
