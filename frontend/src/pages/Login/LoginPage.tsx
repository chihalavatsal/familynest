import { useState, useRef, useEffect } from 'react';
import { Link, useNavigate, useSearchParams, useLocation } from 'react-router-dom';
import { Mail, Lock, Eye, EyeOff, Home } from 'lucide-react';
import { useAuth } from '../../store/AuthContext';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { InlineError } from '../../components/feedback';
import type { ApiError } from '../../types';

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const location = useLocation();
  const emailRef = useRef<HTMLInputElement>(null);

  const from = (location.state as { from?: Location })?.from?.pathname ?? '/dashboard';

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<{ email?: string; password?: string }>({});
  const [apiError, setApiError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    emailRef.current?.focus();
  }, []);

  const validate = () => {
    const errs: typeof errors = {};
    if (!email.trim()) errs.email = 'Email is required';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))
      errs.email = 'Enter a valid email address';
    if (!password) errs.password = 'Password is required';
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setApiError(null);
    if (!validate()) return;

    setLoading(true);
    try {
      await login(email.trim(), password);
      navigate(from, { replace: true });
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      setApiError(apiErr.message ?? 'Sign in failed. Please try again.');
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

      {/* Card */}
      <div className="flex-1 flex items-center justify-center px-4 py-8">
        <div className="w-full max-w-[400px]">
          <div className="bg-white rounded-2xl border border-stone-100 shadow-[0_2px_20px_rgba(0,0,0,0.07)] p-7 sm:p-8">
            {/* Heading */}
            <div className="mb-7">
              <h1 className="text-[22px] font-serif font-semibold text-stone-900 tracking-tight mb-1">
                Welcome back
              </h1>
              <p className="text-[14px] text-stone-500">
                Sign in to your private family space.
              </p>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} noValidate className="space-y-4">
              
            {searchParams.get('reset') === 'success' && (
              <div className="mb-4 p-3 bg-green-50 text-green-700 text-[13px] rounded-xl border border-green-200">
                Password reset successfully. You can now sign in with your new password.
              </div>
            )}

                {apiError && <InlineError message={apiError} />}

              <Input
                ref={emailRef}
                label="Email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  if (errors.email) setErrors((prev) => ({ ...prev, email: undefined }));
                }}
                error={errors.email}
                required
                autoComplete="email"
                leftIcon={<Mail className="w-4 h-4" />}
              />

              <Input
                label="Password"
                type={showPassword ? 'text' : 'password'}
                placeholder="Your password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (errors.password) setErrors((prev) => ({ ...prev, password: undefined }));
                }}
                error={errors.password}
                required
                autoComplete="current-password"
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

              <div className="flex justify-end mt-[-8px] mb-2">
                <Link to="/forgot-password" className="text-[12px] font-medium text-[#92614a] hover:underline">
                  Forgot password?
                </Link>
              </div>

              <Button
                type="submit"
                fullWidth
                size="lg"
                loading={loading}
                className="mt-2"
              >
                Sign in
              </Button>

              
            </form>

            <p className="text-center text-[13px] text-stone-500 mt-5">
              Don't have an account?{' '}
              <Link
                to="/register"
                className="text-[#92614a] font-medium hover:underline"
              >
                Create one
              </Link>
            </p>
          </div>

          <p className="text-center text-[12px] text-stone-400 mt-5">
            Your family's memories are private and secure.
          </p>
        </div>
      </div>
    </div>
  );
}
