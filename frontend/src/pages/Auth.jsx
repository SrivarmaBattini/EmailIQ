import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Mail, Sparkles, LogIn, UserPlus } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuth } from '../context/AuthContext'

export default function Auth() {
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const { login, signup } = useAuth()
  const nav = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (isLogin) {
        await login(email, password)
      } else {
        await signup(email, password)
      }
      nav('/dashboard') // redirect after login/signup
    } catch (err) {
      toast.error(err.message)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden bg-slate-50">
      {/* Background decoration */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[50%] rounded-full opacity-10 blur-[120px] pointer-events-none bg-brand-500 animate-float" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[50%] rounded-full opacity-10 blur-[120px] pointer-events-none bg-blue-500 animate-float" style={{ animationDelay: '-3s' }} />

      <div className="glass-panel w-full max-w-md p-8 rounded-3xl relative z-10 shadow-float">
        <div className="text-center mb-8">
          <div className="w-12 h-12 rounded-xl flex items-center justify-center gradient-bg mx-auto mb-4 shadow-glow-primary">
            <Mail size={24} color="white" />
          </div>
          <h1 className="text-2xl font-bold text-slate-800 tracking-tight">Welcome to <span className="gradient-text font-extrabold">EmailIQ</span></h1>
          <p className="text-slate-500 text-sm mt-2">
            {isLogin ? 'Sign in to access your dashboard' : 'Create an account to start analyzing'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1.5 ml-1">Work Email</label>
            <input 
              type="email" 
              required
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="you@company.com"
              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-700
                         placeholder-slate-400 focus:outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 transition-all"
            />
          </div>
          
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1.5 ml-1">Password</label>
            <input 
              type="password" 
              required
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-700
                         placeholder-slate-400 focus:outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 transition-all"
            />
          </div>

          <button type="submit" className="btn-primary w-full mt-4 py-3.5">
            {isLogin ? (
              <><LogIn size={18} /> Sign In</>
            ) : (
              <><UserPlus size={18} /> Create Account</>
            )}
          </button>
        </form>

        <div className="mt-6 pt-6 border-t border-slate-100 text-center">
          <p className="text-sm text-slate-500">
            {isLogin ? "Don't have an account? " : "Already have an account? "}
            <button 
              onClick={() => setIsLogin(!isLogin)}
              className="text-brand-600 font-semibold hover:text-brand-700 transition-colors">
              {isLogin ? 'Sign up' : 'Sign in'}
            </button>
          </p>
        </div>
      </div>
    </div>
  )
}
