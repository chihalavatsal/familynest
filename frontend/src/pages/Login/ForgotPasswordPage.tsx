import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, Home } from 'lucide-react';
import { authApi } from '../../api/auth';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { InlineError } from '../../components/feedback';
import type { ApiError } from '../../types';

export function ForgotPasswordPage() {
  const navigate = useNavigate();

  const [step, setStep] = useState<1 | 2>(1);
  const [email, setEmail] = useState('');
  const [otpCode, setOtpCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [apiError, setApiError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleRequestOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setApiError(null);
    if (!email.trim()) return;

    setLoading(true);
    try {
      await authApi.forgotPassword({ email: email.trim() });
      setStep(2);
      setSuccessMsg(`We sent a password reset code to ${email}.`);
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      setApiError(apiErr.message ?? 'Failed to request reset code.');
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setApiError(null);
    if (!otpCode.trim() || !newPassword.trim()) return;
    
    if (newPassword.length < 8) {
      setApiError("Password must be at least 8 characters");
      return;
    }

    setLoading(true);
    try {
      await authApi.resetPassword({
        email: email.trim(),
        otp_code: otpCode.trim(),
        new_password: newPassword
      });
      // Success!
      navigate('/login?reset=success');
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      setApiError(apiErr.message ?? 'Failed to reset password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#fdf9f6] flex flex-col">
      <header className="px-6 py-5 flex items-center gap-3">
        <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-[#a0714f] to-[#7d5240] flex items-center justify-center">
          <Home className="w-4 h-4 text-white" strokeWidth={2} />
        </div>
        <span className="text-[15px] font-serif font-semibold text-stone-900 tracking-tight">
          FamilyNest
        </span>
      </header>

      <div className="flex-1 flex items-center justify-center px-4 py-8">
        <div className="w-full max-w-[400px]">
          <div className="bg-white rounded-2xl border border-stone-100 shadow-[0_2px_20px_rgba(0,0,0,0.07)] p-7 sm:p-8">
            <div className="mb-7">
              <h1 className="text-[22px] font-serif font-semibold text-stone-900 tracking-tight mb-1">
                Reset your password
              </h1>
              <p className="text-[14px] text-stone-500">
                {step === 1 ? "Enter your email to receive a reset code." : successMsg}
              </p>
            </div>

            {step === 1 ? (
              <form onSubmit={handleRequestOtp} noValidate className="space-y-4">
                {apiError && <InlineError message={apiError} />}

                <Input
                  label="Email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  leftIcon={<Mail className="w-4 h-4" />}
                />

                <Button type="submit" fullWidth size="lg" loading={loading} className="mt-2">
                  Send reset code
                </Button>
              </form>
            ) : (
              <form onSubmit={handleResetPassword} noValidate className="space-y-4">
                {apiError && <InlineError message={apiError} />}

                <Input
                  label="Reset Code"
                  type="text"
                  placeholder="123456"
                  value={otpCode}
                  onChange={(e) => setOtpCode(e.target.value)}
                  required
                />
                
                <Input
                  label="New Password"
                  type="password"
                  placeholder="At least 8 characters"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                  leftIcon={<Lock className="w-4 h-4" />}
                />

                <Button type="submit" fullWidth size="lg" loading={loading} className="mt-2">
                  Reset Password
                </Button>
              </form>
            )}

            <p className="text-center text-[13px] text-stone-500 mt-5">
              Remembered your password?{' '}
              <Link to="/login" className="text-[#92614a] font-medium hover:underline">
                Back to sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
