import type { ApiError } from '../types';

const BASE_URL = import.meta.env.VITE_API_URL || 'https://familynest-uwxe.onrender.com/api/v1';

// Token storage keys — minimise what's in localStorage
const ACCESS_TOKEN_KEY = 'fn_at';
const REFRESH_TOKEN_KEY = 'fn_rt';

// ============================================================
// Token helpers
// ============================================================

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function setTokens(access: string, refresh: string): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, access);
  localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
}

export function clearTokens(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

// ============================================================
// Error normalisation
// ============================================================

function normalizeError(status: number, body: unknown): ApiError {
  if (typeof body === 'object' && body !== null) {
    const b = body as Record<string, unknown>;

    // FastAPI validation error
    if (Array.isArray(b.detail)) {
      const fieldErrors: Record<string, string> = {};
      for (const err of b.detail as Array<{ loc: string[]; msg: string }>) {
        const field = err.loc[err.loc.length - 1];
        fieldErrors[field] = err.msg;
      }
      return { status, message: 'Validation error', fieldErrors };
    }

    // FastAPI string detail
    if (typeof b.detail === 'string') {
      return { status, message: b.detail };
    }
  }

  const defaultMessages: Record<number, string> = {
    400: 'Invalid request',
    401: 'Your session has expired. Please sign in again.',
    403: 'You do not have permission to do that.',
    404: 'Not found.',
    409: 'A conflict occurred. Please try again.',
    422: 'Validation error.',
    429: 'Too many requests. Please slow down.',
    500: 'Something went wrong on our end. Please try again.',
    503: 'Service unavailable.',
  };

  return {
    status,
    message: defaultMessages[status] ?? 'An unexpected error occurred.',
  };
}

// ============================================================
// Refresh logic (called once, shared via promise)
// ============================================================

let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  if (refreshPromise) return refreshPromise;

  refreshPromise = (async () => {
    const refreshToken = getRefreshToken();
    if (!refreshToken) return null;

    try {
      const res = await fetch(`${BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!res.ok) {
        clearTokens();
        return null;
      }

      const data = await res.json();
      if (data.access_token) {
        // Re-store: refresh may rotate
        setTokens(data.access_token, data.refresh_token ?? refreshToken);
        return data.access_token as string;
      }
      clearTokens();
      return null;
    } catch {
      clearTokens();
      return null;
    } finally {
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

// ============================================================
// Core request function
// ============================================================

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

interface RequestOptions {
  method?: HttpMethod;
  body?: unknown;
  requireAuth?: boolean;
  signal?: AbortSignal;
}

export async function apiRequest<T = unknown>(
  path: string,
  options: RequestOptions = {}
): Promise<T> {
  const { method = 'GET', body, requireAuth = true, signal } = options;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  };

  if (requireAuth) {
    const token = getAccessToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;
  }

  const doRequest = async (authHeader?: string): Promise<Response> => {
    if (authHeader) headers['Authorization'] = authHeader;
    try {
      return await fetch(`${BASE_URL}${path}`, {
        method,
        headers,
        body: body !== undefined ? JSON.stringify(body) : undefined,
        signal,
      });
    } catch (error) {
      if (!navigator.onLine || (error instanceof TypeError && error.message.includes('fetch'))) {
        throw { status: 0, message: "You're offline. We couldn't reach FamilyNest. Check your connection and try again." } as ApiError;
      }
      throw error;
    }
  };

  let res = await doRequest();

  // Auto-refresh on 401
  if (res.status === 401 && requireAuth) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      res = await doRequest(`Bearer ${newToken}`);
    } else {
      // Trigger global sign-out
      window.dispatchEvent(new CustomEvent('fn:auth:expired'));
      throw { status: 401, message: 'Session expired. Please sign in again.' } as ApiError;
    }
  }

  if (!res.ok) {
    let body: unknown;
    try { body = await res.json(); } catch { body = null; }
    throw normalizeError(res.status, body);
  }

  // 204 No Content
  if (res.status === 204) return undefined as T;

  return res.json() as Promise<T>;
}

// ============================================================
// Convenience wrappers
// ============================================================

export const api = {
  get: <T>(path: string, opts?: Omit<RequestOptions, 'method' | 'body'>) =>
    apiRequest<T>(path, { ...opts, method: 'GET' }),

  post: <T>(path: string, body?: unknown, opts?: Omit<RequestOptions, 'method'>) =>
    apiRequest<T>(path, { ...opts, method: 'POST', body }),

  patch: <T>(path: string, body?: unknown, opts?: Omit<RequestOptions, 'method'>) =>
    apiRequest<T>(path, { ...opts, method: 'PATCH', body }),

  put: <T>(path: string, body?: unknown, opts?: Omit<RequestOptions, 'method'>) =>
    apiRequest<T>(path, { ...opts, method: 'PUT', body }),

  delete: <T>(path: string, opts?: Omit<RequestOptions, 'method' | 'body'>) =>
    apiRequest<T>(path, { ...opts, method: 'DELETE' }),
};
