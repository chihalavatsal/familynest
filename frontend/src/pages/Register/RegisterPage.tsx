import { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Mail, Lock, Eye, EyeOff, User, Home } from 'lucide-react';
// import { useAuth } from '../../store/AuthContext';
import { authApi } from '../../api/auth';
import { setTokens } from '../../api/client';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { InlineError } from '../../components/feedback';
import type { ApiError } from '../../types';

export function RegisterPage() {
  // const { register } = useAuth();
  // const navigate = useNavigate();
  const emailRef = useRef<HTMLInputElement>(null);

  const [displayName, setDisplayName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [apiError, setApiError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [showOtp, setShowOtp] = useState(false);
  const [otpCode, setOtpCode] = useState('');

  useEffect(() => {
    emailRef.current?.focus();
  }, []);

  const validate = () => {
    const errs: Record<string, string> = {};
    if (!email.trim()) errs.email = 'Email is required';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))
      errs.email = 'Enter a valid email address';
    if (!password) errs.password = 'Password is required';
    else if (password.length < 8) errs.password = 'Password must be at least 8 characters';
    else if (password.length > 72) errs.password = 'Password is too long';
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setApiError(null);
    if (!validate()) return;

    setLoading(true);
    try {
      await authApi.register({
        email: email.trim(),
        password,
        display_name: displayName.trim() || undefined,
      });
      setShowOtp(true);
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      setApiError(apiErr.message ?? 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  
  const handleResendOtp = async () => {
    if (!email.trim()) return;
    try {
      await authApi.resendOtp({ email: email.trim() });
      setApiError(null);
      // Could show a success toast here
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      setApiError(apiErr.message ?? 'Failed to resend code.');
    }
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setApiError(null);
    if (!otpCode.trim()) return;
    
    setLoading(true);
    try {
      const tokens = await authApi.verifyOtp({
        email: email.trim(),
        otp_code: otpCode.trim(),
      });
      setTokens(tokens.access_token, tokens.refresh_token);
      window.location.href = '/dashboard';
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      setApiError(apiErr.message ?? 'Verification failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#fdf9f6] flex flex-col">
      {/* Header */}
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
                Create your account
              </h1>
              <p className="text-[14px] text-stone-500">
                A private space for your family's story.
              </p>
            </div>

            {/* Important note */}
            <div className="mb-5 p-3.5 rounded-xl bg-[#fdf4ed] border border-[#e8d9cc] text-[13px] text-[#7d5240] leading-relaxed">
              <strong className="font-semibold">Note:</strong> Creating an account doesn't automatically create a person record. You'll connect to your family identity after signing in.
            </div>

            
            {showOtp ? (
              <form onSubmit={handleVerifyOtp} noValidate className="space-y-4">
                <div className="mb-4">
                  <h2 className="text-[18px] font-semibold text-stone-900">Verify your email</h2>
                  <p className="text-[14px] text-stone-500 mt-1">
                    We just sent a 6-digit code to {email}. Please enter it below.
                  </p>
                </div>
                {apiError && <InlineError message={apiError} />}
                <Input
                  label="Verification Code"
                  type="text"
                  placeholder="123456"
                  value={otpCode}
                  onChange={(e) => setOtpCode(e.target.value)}
                  required
                />
                
                <Button type="submit" fullWidth size="lg" loading={loading} className="mt-2">
                  Verify & Sign in
                </Button>
                
                <div className="text-center mt-3">
                  <button type="button" onClick={handleResendOtp} className="text-[13px] text-[#92614a] font-medium hover:underline">
                    Didn't receive a code? Resend
                  </button>
                </div>

              </form>
            ) : (<form onSubmit={handleSubmit} noValidate className="space-y-4">

              {apiError && <InlineError message={apiError} />}

              <Input
                label="Display name"
                type="text"
                placeholder="Your name (optional)"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                autoComplete="name"
                leftIcon={<User className="w-4 h-4" />}
              />

              <Input
                ref={emailRef}
                label="Email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  if (errors.email) setErrors((p) => ({ ...p, email: '' }));
                }}
                error={errors.email}
                required
                autoComplete="email"
                leftIcon={<Mail className="w-4 h-4" />}
              />

              <Input
                label="Password"
                type={showPassword ? 'text' : 'password'}
                placeholder="At least 8 characters"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (errors.password) setErrors((p) => ({ ...p, password: '' }));
                }}
                error={errors.password}
                required
                autoComplete="new-password"
                hint="8–72 characters"
                leftIcon={<Lock className="w-4 h-4" />}
                rightIcon={
                  <button
                    type="button"
                    onClick={() => setShowPassword((s) => !s)}
                    className="text-stone-400 hover:text-stone-600 transition-colors"
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                    tabIndex={-1}
                  >
                    {showPassword ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                }
              />

              <Button
                type="submit"
                fullWidth
                size="lg"
                loading={loading}
                className="mt-2"
              >
                Create account
              </Button>

              
            </form>)}

            <p className="text-center text-[13px] text-stone-500 mt-5">
              Already have an account?{' '}
              <Link
                to="/login"
                className="text-[#92614a] font-medium hover:underline"
              >
                Sign in
              </Link>
            </p>
          </div>

          <p className="text-center text-[12px] text-stone-400 mt-5">
            No public profiles. No data sharing. Private by design.
          </p>
        </div>
      </div>
    </div>
  );
}
