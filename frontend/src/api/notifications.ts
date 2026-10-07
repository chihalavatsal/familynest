import { api } from './client';
import type { NotificationListResponse, NotificationResponse } from '../types';

export const notificationsApi = {
  list: (unread?: boolean, page: number = 1, page_size: number = 20) => {
    const params = new URLSearchParams();
    if (unread !== undefined) params.append('unread', unread.toString());
    params.append('page', page.toString());
    params.append('page_size', page_size.toString());
    return api.get<NotificationListResponse>(`/notifications?${params.toString()}`);
  },

  markRead: (id: string) => api.post<NotificationResponse>(`/notifications/${id}/read`),

  markUnread: (id: string) => api.post<NotificationResponse>(`/notifications/${id}/unread`),

  markAllRead: () => api.post<void>('/notifications/read-all'),

  dismiss: (id: string) => api.post<void>(`/notifications/${id}/dismiss`),

  getPreferences: () => api.get<any>('/notifications/preferences'),

  updatePreferences: (data: any) => api.patch<any>('/notifications/preferences', data),
};
