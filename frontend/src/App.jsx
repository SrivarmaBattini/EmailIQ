import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Navbar from './components/layout/Navbar'
import Landing from './pages/Landing'
import Analyser from './pages/Analyser'
import ThreadAnalyser from './pages/ThreadAnalyser'
import Dashboard from './pages/Dashboard'
import Coach from './pages/Coach'
import Auth from './pages/Auth'
import { AuthProvider, useAuth } from './context/AuthContext'

function ProtectedRoute({ children }) {
  const { user } = useAuth()
  if (!user) {
    return <Navigate to="/auth" replace />
  }
  return children
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster
          position="top-right"
          toastOptions={{
            style: { background: '#ffffff', color: '#1e293b', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }
          }}
        />
        <Navbar />
        <Routes>
          <Route path="/"        element={<Landing />} />
          <Route path="/auth"    element={<Auth />} />
          <Route path="/analyse" element={<ProtectedRoute><Analyser /></ProtectedRoute>} />
          <Route path="/thread"  element={<ProtectedRoute><ThreadAnalyser /></ProtectedRoute>} />
          <Route path="/coach"   element={<ProtectedRoute><Coach /></ProtectedRoute>} />
          <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

