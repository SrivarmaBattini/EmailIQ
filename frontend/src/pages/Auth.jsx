import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Mail, LogIn, UserPlus, KeyRound, CheckCircle2, XCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuth } from '../context/AuthContext'

export default function Auth() {
  const [mode, setMode] = useState('login') // 'login', 'signup', 'forgot'
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const { login, signup, resetPassword } = useAuth()
  const nav = useNavigate()

  // Password validation states
  const [passValid, setPassValid] = useState({
    length: false,
    upper: false,
    number: false,
    special: false
  })

  useEffect(() => {
    setPassValid({
      length: password.length >= 8,
      upper: /[A-Z]/.test(password),
      number: /[0-9]/.test(password),
      special: /[^A-Za-z0-9]/.test(password)
    })
  }, [password])

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    try {
      if (mode === 'forgot') {
        await resetPassword(email)
        toast.success("Password reset link sent to your email!")
        setMode('login')
        return
      }

      if (mode === 'signup') {
        const isValid = Object.values(passValid).every(Boolean)
        if (!isValid) {
          toast.error("Please meet all password requirements.")
          return
        }
        if (!name.trim()) {
          toast.error("Please enter your name.")
          return
        }
        await signup(email, password, name)
        toast.success("Account created successfully!")
        nav('/dashboard')
        return
      }

      if (mode === 'login') {
        await login(email, password)
        toast.success("Welcome back!")
        nav('/dashboard')
      }
    } catch (err) {
      toast.error(err.message)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden bg-slate-50">
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[50%] rounded-full opacity-10 blur-[120px] pointer-events-none bg-brand-500 animate-float" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[50%] rounded-full opacity-10 blur-[120px] pointer-events-none bg-blue-500 animate-float" style={{ animationDelay: '-3s' }} />

      <div className="glass-panel w-full max-w-md p-8 rounded-3xl relative z-10 shadow-float">
        <div className="text-center mb-8">
          <div className="w-12 h-12 rounded-xl flex items-center justify-center gradient-bg mx-auto mb-4 shadow-glow-primary">
            <Mail size={24} color="white" />
          </div>
          <h1 className="text-2xl font-bold text-slate-800 tracking-tight">
            {mode === 'forgot' ? 'Reset Password' : <>Welcome to <span className="gradient-text font-extrabold">EmailIQ</span></>}
          </h1>
          <p className="text-slate-500 text-sm mt-2">
            {mode === 'login' && 'Sign in to access your dashboard'}
            {mode === 'signup' && 'Create an account to start analyzing'}
            {mode === 'forgot' && 'Enter your email to receive a reset link'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          
          {mode === 'signup' && (
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5 ml-1">Full Name</label>
              <input 
                type="text" 
                required
                value={name}
                onChange={e => setName(e.target.value)}
                placeholder="John Doe"
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-700 placeholder-slate-400 focus:outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 transition-all"
              />
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1.5 ml-1">Work Email</label>
            <input 
              type="email" 
              required
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="you@company.com"
              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-700 placeholder-slate-400 focus:outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 transition-all"
            />
          </div>
          
          {mode !== 'forgot' && (
            <div>
              <div className="flex justify-between items-center mb-1.5 ml-1 pr-1">
                <label className="block text-xs font-semibold text-slate-600">Password</label>
                {mode === 'login' && (
                  <button 
                    type="button"
                    onClick={() => setMode('forgot')}
                    className="text-xs font-semibold text-brand-600 hover:text-brand-700"
                  >
                    Forgot Password?
                  </button>
                )}
              </div>
              <input 
                type="password" 
                required
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-700 placeholder-slate-400 focus:outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 transition-all"
              />

              {mode === 'signup' && password.length > 0 && (
                <div className="mt-3 p-3 bg-slate-50 rounded-lg border border-slate-100 text-xs flex flex-col gap-2">
                  <div className={`flex items-center gap-2 ${passValid.length ? 'text-green-600' : 'text-slate-500'}`}>
                    {passValid.length ? <CheckCircle2 size={14}/> : <XCircle size={14}/>} At least 8 characters
                  </div>
                  <div className={`flex items-center gap-2 ${passValid.upper ? 'text-green-600' : 'text-slate-500'}`}>
                    {passValid.upper ? <CheckCircle2 size={14}/> : <XCircle size={14}/>} One uppercase letter
                  </div>
                  <div className={`flex items-center gap-2 ${passValid.number ? 'text-green-600' : 'text-slate-500'}`}>
                    {passValid.number ? <CheckCircle2 size={14}/> : <XCircle size={14}/>} One number
                  </div>
                  <div className={`flex items-center gap-2 ${passValid.special ? 'text-green-600' : 'text-slate-500'}`}>
                    {passValid.special ? <CheckCircle2 size={14}/> : <XCircle size={14}/>} One special character
                  </div>
                </div>
              )}
            </div>
          )}

          <button type="submit" className="btn-primary w-full mt-4 py-3.5 flex items-center justify-center gap-2">
            {mode === 'login' && <><LogIn size={18} /> Sign In</>}
            {mode === 'signup' && <><UserPlus size={18} /> Create Account</>}
            {mode === 'forgot' && <><KeyRound size={18} /> Send Reset Link</>}
          </button>
        </form>

        <div className="mt-6 pt-6 border-t border-slate-100 text-center">
          <p className="text-sm text-slate-500">
            {mode === 'login' && (
              <>Don't have an account? <button onClick={() => setMode('signup')} className="text-brand-600 font-semibold hover:text-brand-700">Sign up</button></>
            )}
            {mode === 'signup' && (
              <>Already have an account? <button onClick={() => setMode('login')} className="text-brand-600 font-semibold hover:text-brand-700">Sign in</button></>
            )}
            {mode === 'forgot' && (
              <>Remember your password? <button onClick={() => setMode('login')} className="text-brand-600 font-semibold hover:text-brand-700">Back to Login</button></>
            )}
          </p>
        </div>
      </div>
    </div>
  )
}
