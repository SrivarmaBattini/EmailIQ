import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { KeyRound, CheckCircle2, XCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuth } from '../context/AuthContext'

export default function ResetPassword() {
  const [password, setPassword] = useState('')
  const { updatePassword } = useAuth()
  const nav = useNavigate()

  const passValid = {
    length: password.length >= 8,
    upper: /[A-Z]/.test(password),
    number: /[0-9]/.test(password),
    special: /[^A-Za-z0-9]/.test(password)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    const isValid = Object.values(passValid).every(Boolean)
    if (!isValid) {
      toast.error("Please meet all password requirements.")
      return
    }

    try {
      await updatePassword(password)
      toast.success("Password updated successfully!")
      nav('/dashboard')
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
            <KeyRound size={24} color="white" />
          </div>
          <h1 className="text-2xl font-bold text-slate-800 tracking-tight">Set New Password</h1>
          <p className="text-slate-500 text-sm mt-2">
            Please enter your new secure password below.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1.5 ml-1">New Password</label>
            <input 
              type="password" 
              required
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-700 placeholder-slate-400 focus:outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 transition-all"
            />

            {password.length > 0 && (
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

          <button type="submit" className="btn-primary w-full mt-4 py-3.5 flex items-center justify-center gap-2">
            <KeyRound size={18} /> Update Password
          </button>
        </form>
      </div>
    </div>
  )
}
