import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './store/AuthContext';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ToastProvider } from './components/ui/Toast';
import { ProtectedRoute, GuestRoute } from './routes/ProtectedRoute';
import { AppShell } from './components/layout/AppShell';

import { MemoriesPage } from './pages/Memories/MemoriesPage';
import { MemoryDetailPage } from './pages/Memories/MemoryDetailPage';
import { MemoryCreatePage } from './pages/Memories/MemoryCreatePage';

import { LoginPage } from './pages/Login/LoginPage';
import { RegisterPage } from './pages/Register/RegisterPage';
import { AuthCallbackPage } from './pages/Login/AuthCallbackPage';
import { ForgotPasswordPage } from './pages/Login/ForgotPasswordPage';
import { DashboardPage } from './pages/Dashboard/DashboardPage';
import { ProfilePage } from './pages/Profile/ProfilePage';
import { PrivacyPage } from './pages/Privacy/PrivacyPage';
import { FamiliesPage } from './pages/Families/FamiliesPage';
import { FamilyDetailPage } from './pages/FamilyDetail/FamilyDetailPage';
import { FamilyTreePage } from './pages/Tree/FamilyTreePage';
import { PeoplePage } from './pages/People/PeoplePage';
import { PersonDetailPage } from './pages/People/PersonDetailPage';
import { NotificationsPage } from './pages/Notifications/NotificationsPage';
import { InvitationsPage } from './pages/Invitations/InvitationsPage';
import { EventsPage } from './pages/Events/EventsPage';
import { EventDetailPage } from './pages/Events/EventDetailPage';
import { ActivityPage } from './pages/Activity/ActivityPage';
import { SearchResultsPage } from './pages/Search/SearchResultsPage';

export 
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      refetchOnWindowFocus: true,
      retry: 1,
    },
  },
});

function App() {
  return (
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ToastProvider>
          <Routes>
            {/* ── Guest-only routes ── */}
            <Route element={<GuestRoute />}>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/forgot-password" element={<ForgotPasswordPage />} />
              <Route path="/register" element={<RegisterPage />} />
            </Route>
            <Route path="/auth/callback" element={<AuthCallbackPage />} />

            {/* ── Protected application routes ── */}
            <Route element={<ProtectedRoute />}>
              <Route element={<AppShell />}>
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/profile" element={<ProfilePage />} />
                <Route path="/privacy" element={<PrivacyPage />} />
                <Route path="/families" element={<FamiliesPage />} />
                <Route path="/families/:familyId" element={<FamilyDetailPage />} />
                <Route path="/tree" element={<FamilyTreePage />} />
                <Route path="/people" element={<PeoplePage />} />
                <Route path="/people/:personId" element={<PersonDetailPage />} />
                <Route path="/notifications" element={<NotificationsPage />} />
                <Route path="/invitations" element={<InvitationsPage />} />
                <Route path="/events" element={<EventsPage />} />
                <Route path="/events/:eventId" element={<EventDetailPage />} />
                <Route path="/activity" element={<ActivityPage />} />
                <Route path="/search" element={<SearchResultsPage />} />
                <Route path="/memories" element={<MemoriesPage />} />
                <Route path="/memories/new" element={<MemoryCreatePage />} />
                <Route path="/memories/:id" element={<MemoryDetailPage />} />
              </Route>
            </Route>

            {/* ── Root / catch-all ── */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </ToastProvider>
      </AuthProvider>
    </QueryClientProvider>
    </BrowserRouter>
  );
}

export default App;
