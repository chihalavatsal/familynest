import React, {
  createContext,
  useContext,
  useEffect,
  useReducer,
  useCallback,
} from 'react';
import type { AuthUser } from '../types';
import { authApi } from '../api/auth';
import { setTokens, clearTokens } from '../api/client';

// ============================================================
// State
// ============================================================

interface AuthState {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

type AuthAction =
  | { type: 'AUTH_LOADING' }
  | { type: 'AUTH_SUCCESS'; user: AuthUser }
  | { type: 'AUTH_ERROR'; error: string }
  | { type: 'AUTH_LOGOUT' }
  | { type: 'AUTH_CLEAR_ERROR' };

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'AUTH_LOADING':
      return { ...state, isLoading: true, error: null };
    case 'AUTH_SUCCESS':
      return {
        user: action.user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };
    case 'AUTH_ERROR':
      return {
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.error,
      };
    case 'AUTH_LOGOUT':
      return {
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      };
    case 'AUTH_CLEAR_ERROR':
      return { ...state, error: null };
    default:
      return state;
  }
}

// ============================================================
// Context
// ============================================================

interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, displayName?: string) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

// ============================================================
// Provider
// ============================================================

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, {
    user: null,
    isAuthenticated: false,
    isLoading: true, // start loading — we'll check session
    error: null,
  });

  // Check existing session on mount
  useEffect(() => {
    const token = localStorage.getItem('fn_at');
    if (!token) {
      dispatch({ type: 'AUTH_LOGOUT' });
      return;
    }

    authApi
      .me()
      .then((user) => dispatch({ type: 'AUTH_SUCCESS', user }))
      .catch(() => {
        clearTokens();
        dispatch({ type: 'AUTH_LOGOUT' });
      });
  }, []);

  // Listen for global session expiry
  useEffect(() => {
    const handle = () => {
      clearTokens();
      dispatch({ type: 'AUTH_LOGOUT' });
    };
    window.addEventListener('fn:auth:expired', handle);
    return () => window.removeEventListener('fn:auth:expired', handle);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    
    try {
      const tokens = await authApi.login({ email, password });
      setTokens(tokens.access_token, tokens.refresh_token);
      const user = await authApi.me();
      dispatch({ type: 'AUTH_SUCCESS', user });
    } catch (err: unknown) {
      const message =
        (err as { message?: string })?.message ?? 'Sign in failed.';
      dispatch({ type: 'AUTH_ERROR', error: message });
      throw err;
    }
  }, []);

  const register = useCallback(
    async (email: string, password: string, displayName?: string) => {
      
      try {
        await authApi.register({
          email,
          password,
          display_name: displayName,
        });
        // Auto-login after registration
        const tokens = await authApi.login({ email, password });
        setTokens(tokens.access_token, tokens.refresh_token);
        const user = await authApi.me();
        dispatch({ type: 'AUTH_SUCCESS', user });
      } catch (err: unknown) {
        const message =
          (err as { message?: string })?.message ?? 'Registration failed.';
        dispatch({ type: 'AUTH_ERROR', error: message });
        throw err;
      }
    },
    []
  );

  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } catch {
      // Best-effort logout
    } finally {
      clearTokens();
      dispatch({ type: 'AUTH_LOGOUT' });
    }
  }, []);

  const clearError = useCallback(() => dispatch({ type: 'AUTH_CLEAR_ERROR' }), []);

  return (
    <AuthContext.Provider value={{ ...state, login, register, logout, clearError }}>
      {children}
    </AuthContext.Provider>
  );
}

// ============================================================
// Hook
// ============================================================

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
