import type { NotificationResponse } from '../types';

export function getNotificationNavigationTarget(notification: NotificationResponse): string | null {
  const { target_type, target_id } = notification;

  if (!target_type || !target_id) {
    return null;
  }

  switch (target_type) {
    case 'family':
      return `/families/${target_id}`;
    case 'person':
      return `/people/${target_id}`;
    case 'user':
      // Currently we might not have a public user profile route, but if we do it would be here.
      // If none exists, return null.
      return null;
    default:
      return null;
  }
}
