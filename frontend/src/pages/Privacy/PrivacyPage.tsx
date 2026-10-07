import { useEffect, useState } from 'react';
import { Shield } from 'lucide-react';
import { privacyApi } from '../../api/privacy';
import { familiesApi } from '../../api/families';
import type { PersonPrivacySettingsResponse, FamilyPrivacySettingsResponse, FamilyResponse } from '../../types';
import { Card } from '../../components/ui/Card';
import { useToast } from '../../components/ui/Toast';
import { ListSkeleton } from '../../components/feedback';
import { OnboardingPrompt } from '../Dashboard/OnboardingPrompt';

export function PrivacyPage() {
  const { success, error } = useToast();
  
  
  const [profileSettings, setProfileSettings] = useState<PersonPrivacySettingsResponse | null>(null);
  const [families, setFamilies] = useState<FamilyResponse[]>([]);
  const [familySettings, setFamilySettings] = useState<Record<string, FamilyPrivacySettingsResponse>>({});
  const [loading, setLoading] = useState(true);
  const [noPerson, setNoPerson] = useState(false);
  const [savingProfile, setSavingProfile] = useState(false);
  const [savingFamily, setSavingFamily] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const [profRes, famRes] = await Promise.all([
          privacyApi.getProfilePrivacy(),
          familiesApi.list()
        ]);
        setProfileSettings(profRes);
        setFamilies(famRes.items || []);
        
        const settingsMap: Record<string, FamilyPrivacySettingsResponse> = {};
        for (const f of (famRes.items || [])) {
          if (true) {
            try {
              const fs = await privacyApi.getFamilySettings(f.id);
              settingsMap[f.id] = fs;
            } catch (e) {
              // Ignore if not authorized or error
            }
          }
        }
        setFamilySettings(settingsMap);
      } catch (err: any) {
        if (err.message && err.message.includes("No claimed person found")) {
          setNoPerson(true);
        } else {
          error(err.message || 'Failed to load privacy settings');
        }
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleProfileUpdate = async (field: keyof PersonPrivacySettingsResponse, value: string) => {
    if (!profileSettings) return;
    try {
      setSavingProfile(true);
      const res = await privacyApi.updateProfilePrivacy({ [field]: value });
      setProfileSettings(res);
      success('Profile privacy updated');
    } catch (err: any) {
      error(err.message || 'Failed to update settings');
    } finally {
      setSavingProfile(false);
    }
  };

  const handleFamilyUpdate = async (familyId: string, field: keyof FamilyPrivacySettingsResponse, value: any) => {
    if (!familySettings[familyId]) return;
    try {
      setSavingFamily(familyId);
      const res = await privacyApi.updateFamilySettings(familyId, { [field]: value });
      setFamilySettings(prev => ({ ...prev, [familyId]: res }));
      success('Family privacy updated');
    } catch (err: any) {
      error(err.message || 'Failed to update family settings');
    } finally {
      setSavingFamily(null);
    }
  };

  
  if (noPerson) {
    return (
      <div className="max-w-3xl mx-auto pt-8">
        <OnboardingPrompt onComplete={() => window.location.reload()} />
      </div>
    );
  }

  if (loading) return <div className="p-8 max-w-3xl mx-auto"><ListSkeleton rows={5} /></div>;

  return (
    <div className="max-w-3xl mx-auto py-8 px-4 sm:px-6">
      <div className="flex items-center gap-3 mb-8">
        <div className="w-10 h-10 rounded-xl bg-[#e6d8cf]/30 flex items-center justify-center text-[#92614a]">
          <Shield className="w-5 h-5" />
        </div>
        <h1 className="text-2xl font-serif text-stone-900">Privacy Center</h1>
      </div>

      <div className="space-y-12">
        {/* Profile Privacy */}
        <section>
          <h2 className="text-lg font-semibold text-stone-900 mb-4">My Profile Privacy</h2>
          <Card className="divide-y divide-stone-100">
            {profileSettings && ['phone_visibility', 'email_visibility', 'dob_visibility', 'bio_visibility'].map((field) => (
              <div key={field} className="p-4 flex items-center justify-between">
                <div>
                  <p className="font-medium text-sm text-stone-900">
                    {field.replace('_visibility', '').replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} Visibility
                  </p>
                  <p className="text-xs text-stone-500 mt-1">Control who can see this on your profile.</p>
                </div>
                <select
                  value={(profileSettings as any)[field]}
                  onChange={(e) => handleProfileUpdate(field as any, e.target.value)}
                  disabled={savingProfile}
                  className="text-sm rounded-md border-stone-200 focus:border-[#92614a] focus:ring-[#92614a]"
                >
                  <option value="private">Private (Only Me)</option>
                  <option value="family">Family Members</option>
                </select>
              </div>
            ))}
          </Card>
        </section>

        {/* Family Privacy */}
        {families.map(fam => {
          const settings = familySettings[fam.id];
          if (!settings) return null;
          
          return (
            <section key={fam.id}>
              <h2 className="text-lg font-semibold text-stone-900 mb-4">{fam.name} - Family Settings</h2>
              <Card className="divide-y divide-stone-100">
                <div className="p-4 flex items-center justify-between">
                  <div>
                    <p className="font-medium text-sm text-stone-900">Member Discovery</p>
                    <p className="text-xs text-stone-500 mt-1">Allow members to see other family members.</p>
                  </div>
                  <input 
                    type="checkbox"
                    checked={settings.allow_member_discovery}
                    onChange={(e) => handleFamilyUpdate(fam.id, 'allow_member_discovery', e.target.checked)}
                    disabled={savingFamily === fam.id}
                    className="rounded border-stone-300 text-[#92614a] focus:ring-[#92614a]"
                  />
                </div>
                <div className="p-4 flex items-center justify-between">
                  <div>
                    <p className="font-medium text-sm text-stone-900">Default Content Visibility</p>
                    <p className="text-xs text-stone-500 mt-1">Default audience when creating memories or albums.</p>
                  </div>
                  <select
                    value={settings.default_content_visibility}
                    onChange={(e) => handleFamilyUpdate(fam.id, 'default_content_visibility', e.target.value)}
                    disabled={savingFamily === fam.id}
                    className="text-sm rounded-md border-stone-200"
                  >
                    <option value="family">Entire Family</option>
                    <option value="selected_members">Selected Members Only</option>
                  </select>
                </div>
                <div className="p-4 flex items-center justify-between">
                  <div>
                    <p className="font-medium text-sm text-stone-900">Who can invite members?</p>
                  </div>
                  <select
                    value={settings.member_invites_role}
                    onChange={(e) => handleFamilyUpdate(fam.id, 'member_invites_role', e.target.value)}
                    disabled={savingFamily === fam.id}
                    className="text-sm rounded-md border-stone-200"
                  >
                    <option value="member">Any Member</option>
                    <option value="admin">Admins & Owners</option>
                    <option value="owner">Owners Only</option>
                  </select>
                </div>
                <div className="p-4 flex items-center justify-between">
                  <div>
                    <p className="font-medium text-sm text-stone-900">Who can manage members?</p>
                  </div>
                  <select
                    value={settings.member_management_role}
                    onChange={(e) => handleFamilyUpdate(fam.id, 'member_management_role', e.target.value)}
                    disabled={savingFamily === fam.id}
                    className="text-sm rounded-md border-stone-200"
                  >
                    <option value="admin">Admins & Owners</option>
                    <option value="owner">Owners Only</option>
                  </select>
                </div>
              </Card>
            </section>
          );
        })}
      </div>
    </div>
  );
}
