import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { LoginForm } from './Auth/LoginForm.jsx'
import { SignupForm } from './Auth/SignUpForm.jsx'
import TailwindTest from './TailwindTest.jsx'
import PlatformConnect from './PlatformConnect/PlatformConnect.jsx'
import OAuthCallback from './OAuthCallback.jsx'
import Dashboard from './Dashboard/Dashboard.jsx'
import { isAuthenticated } from './Utils/Auth'

// Protected route component
const ProtectedRoute = ({ children }) => {
  // Use our isAuthenticated utility instead of directly checking localStorage
  const authenticated = isAuthenticated();
  
  if (!authenticated) {
    console.log('Access denied: User is not authenticated');
    // Redirect to login if not authenticated
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<LoginForm />} />
      
      {/* Authentication routes */}
      <Route path="/login" element={<LoginForm />} />
      <Route path="/signup" element={<SignupForm />} />
      
      {/* Platform connection routes */}
      <Route 
        path="/platform-connect" 
        element={
          <ProtectedRoute>
            <PlatformConnect />
          </ProtectedRoute>
        } 
      />
      <Route path="/oauth-callback" element={<OAuthCallback />} />
      
      {/* Dashboard route (placeholder) */}
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } 
      />
      
      {/* Test route */}
      <Route path="/test" element={<TailwindTest />} />

      {/* Fallback route */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default AppRoutes