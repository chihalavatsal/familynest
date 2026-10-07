import { api } from './client';
import type { AuthUser, LoginRequest, RegisterRequest, AuthTokens } from '../types';

export const authApi = {
  login: (data: LoginRequest) =>
    api.post<AuthTokens>('/auth/login', data, { requireAuth: false }),

  register: (data: RegisterRequest) =>
    api.post<AuthUser>('/auth/register', data, { requireAuth: false }),

  me: () => api.get<AuthUser>('/auth/me'),

  logout: () => api.post<void>('/auth/logout'),

  resendOtp: (data: { email: string }) =>
    api.post<{ message: string }>('/auth/resend-otp', data, { requireAuth: false }),


  forgotPassword: (data: { email: string }) =>
    api.post<{ message: string }>('/auth/forgot-password', data, { requireAuth: false }),

  resetPassword: (data: { email: string; otp_code: string; new_password: string }) =>
    api.post<{ message: string }>('/auth/reset-password', data, { requireAuth: false }),

  verifyOtp: (data: { email: string; otp_code: string }) =>
    api.post<AuthTokens>('/auth/verify-otp', data, { requireAuth: false }),


  refresh: (refresh_token: string) =>
    api.post<AuthTokens>('/auth/refresh', { refresh_token }, { requireAuth: false }),
};
