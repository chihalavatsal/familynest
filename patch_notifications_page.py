import re

with open("frontend/src/pages/Notifications/NotificationsPage.tsx", "r") as f:
    content = f.read()

# Add useOutletContext
content = content.replace("import { useNavigate } from 'react-router-dom';", "import { useNavigate, useOutletContext } from 'react-router-dom';")

# Add to component
context_str = """  const navigate = useNavigate();
  const { updateUnreadCount } = useOutletContext<{ updateUnreadCount: (c: number | ((prev: number) => number)) => void }>();"""

content = content.replace("  const navigate = useNavigate();", context_str)

# Update mark all read
mark_all_read_new = """  const handleMarkAllRead = async () => {
    try {
      await notificationsApi.markAllRead();
      addToast({ title: 'All notifications marked as read', type: 'success' });
      fetchNotifications();
      updateUnreadCount(0);
    } catch (err) {"""
content = content.replace("""  const handleMarkAllRead = async () => {
    try {
      await notificationsApi.markAllRead();
      addToast({ title: 'All notifications marked as read', type: 'success' });
      fetchNotifications();
    } catch (err) {""", mark_all_read_new)

# Update mark read
mark_read_new = """  const handleMarkRead = async (id: string, currentlyRead: boolean) => {
    if (currentlyRead) return;
    try {
      await notificationsApi.markRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
      updateUnreadCount(prev => Math.max(0, prev - 1));
    } catch (err) {"""
content = content.replace("""  const handleMarkRead = async (id: string, currentlyRead: boolean) => {
    if (currentlyRead) return;
    try {
      await notificationsApi.markRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
    } catch (err) {""", mark_read_new)

# Update dismiss (if it was unread, update badge)
dismiss_new = """  const handleDismiss = async (id: string, currentlyRead: boolean) => {
    try {
      await notificationsApi.dismiss(id);
      addToast({ title: 'Notification dismissed', type: 'success' });
      setNotifications((prev) => prev.filter((n) => n.id !== id));
      setShowDismissConfirm(null);
      if (!currentlyRead) {
        updateUnreadCount(prev => Math.max(0, prev - 1));
      }
    } catch (err) {"""
content = content.replace("""  const handleDismiss = async (id: string) => {
    try {
      await notificationsApi.dismiss(id);
      addToast({ title: 'Notification dismissed', type: 'success' });
      setNotifications((prev) => prev.filter((n) => n.id !== id));
      setShowDismissConfirm(null);
    } catch (err) {""", dismiss_new)

# Update showDismissConfirm to store an object or we can just pass currentlyRead to the dialog?
# Wait, I can find the notification by ID in the array.
content = content.replace("onConfirm={() => handleDismiss(showDismissConfirm)}", "onConfirm={() => { const notif = notifications.find(n => n.id === showDismissConfirm); if (notif) handleDismiss(showDismissConfirm, notif.is_read); }}")

with open("frontend/src/pages/Notifications/NotificationsPage.tsx", "w") as f:
    f.write(content)
