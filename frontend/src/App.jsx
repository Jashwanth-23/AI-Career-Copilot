import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { ResumeProvider } from "./context/ResumeContext";
import { ToastProvider } from "./context/ToastContext";

// Layouts & Components
import DashboardLayout from "./layouts/DashboardLayout";
import ErrorBoundary from "./components/common/ErrorBoundary";

// Pages
import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import MyResumesPage from "./pages/MyResumesPage";
import ResumeUploadPage from "./pages/ResumeUploadPage";
import ResumeAnalysisPage from "./pages/ResumeAnalysisPage";
import AtsScorePage from "./pages/AtsScorePage";
import SkillGapPage from "./pages/SkillGapPage";
import LearningRoadmapPage from "./pages/LearningRoadmapPage";
import JobRecommendationsPage from "./pages/JobRecommendationsPage";
import NotFoundPage from "./pages/NotFoundPage";

// Protected Route Guard Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-surface-950 flex flex-col items-center justify-center space-y-4">
        <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-slate-400 text-sm font-medium">Verifying Session...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

// Public Route Guard (Redirects authenticated users away from /login & /register)
const PublicOnlyRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) return null;
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

function App() {
  return (
    <ErrorBoundary>
      <ToastProvider>
        <AuthProvider>
          <ResumeProvider>
            <Router>
              <Routes>
                {/* Public Pages */}
                <Route path="/" element={<LandingPage />} />
                <Route
                  path="/login"
                  element={
                    <PublicOnlyRoute>
                      <LoginPage />
                    </PublicOnlyRoute>
                  }
                />
                <Route
                  path="/register"
                  element={
                    <PublicOnlyRoute>
                      <RegisterPage />
                    </PublicOnlyRoute>
                  }
                />

                {/* Protected Dashboard Pages */}
                <Route
                  element={
                    <ProtectedRoute>
                      <DashboardLayout />
                    </ProtectedRoute>
                  }
                >
                  <Route path="/dashboard" element={<DashboardPage />} />
                  <Route path="/resumes" element={<MyResumesPage />} />
                  <Route path="/upload" element={<ResumeUploadPage />} />
                  <Route path="/analysis" element={<ResumeAnalysisPage />} />
                  <Route path="/ats" element={<AtsScorePage />} />
                  <Route path="/skill-gap" element={<SkillGapPage />} />
                  <Route path="/roadmap" element={<LearningRoadmapPage />} />
                  <Route path="/jobs" element={<JobRecommendationsPage />} />
                </Route>

                {/* Catch All 404 */}
                <Route path="*" element={<NotFoundPage />} />
              </Routes>
            </Router>
          </ResumeProvider>
        </AuthProvider>
      </ToastProvider>
    </ErrorBoundary>
  );
}

export default App;