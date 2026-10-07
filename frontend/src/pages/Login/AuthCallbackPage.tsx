import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { setTokens } from '../../api/client';

export function AuthCallbackPage() {
  const navigate = useNavigate();
  const location = useLocation();
  // Actually, if we setTokens and then force a reload, it will authenticate.

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const accessToken = params.get('access_token');
    const refreshToken = params.get('refresh_token');

    if (accessToken && refreshToken) {
      setTokens(accessToken, refreshToken);
      // Force a full reload so AuthContext picks up the new tokens and fetches me()
      window.location.href = '/dashboard';
    } else {
      navigate('/login?error=AuthenticationFailed');
    }
  }, [location, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#fdf9f6]">
      <div className="text-stone-500 animate-pulse">Authenticating with Google...</div>
    </div>
  );
}
