import { Link } from 'react-router-dom'
import { Mail, ArrowRight, ShieldCheck, Zap, Activity } from 'lucide-react'

export default function Landing() {
  return (
    <div className="min-h-[calc(100vh-64px)] flex flex-col justify-center items-center px-4 relative overflow-hidden bg-slate-50">
      {/* Background decorations */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[60%] rounded-full opacity-10 blur-[120px] pointer-events-none bg-brand-500 animate-float" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[60%] rounded-full opacity-10 blur-[120px] pointer-events-none bg-blue-500 animate-float" style={{ animationDelay: '-2s' }} />

      <div className="max-w-4xl w-full text-center relative z-10 animate-fade-in">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-brand-50 text-brand-700 font-semibold text-xs uppercase tracking-widest border border-brand-100 mb-8 shadow-sm">
          <SparklesIcon size={14} className="text-brand-500" /> Professional Communication Intelligence
        </div>
        
        <h1 className="text-5xl md:text-7xl font-extrabold text-slate-900 tracking-tight leading-tight mb-6">
          Write emails with <br className="hidden md:block" />
          <span className="gradient-text">Absolute Confidence</span>
        </h1>
        
        <p className="text-lg md:text-xl text-slate-600 mb-10 max-w-2xl mx-auto leading-relaxed">
          EmailIQ is an advanced AI platform that analyzes your professional communication for tone, power dynamics, and passive-aggression. Ensure every message hits the right note.
        </p>

        <div className="flex items-center justify-center gap-4">
          <Link to="/auth" className="btn-primary px-8 py-4 text-base shadow-glow-primary group">
            Sign In / Sign Up <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>

        {/* Feature Highlights */}
        <div className="grid md:grid-cols-3 gap-6 mt-20 text-left">
          {[
            { icon: Activity, title: '7-Dimension Analysis', desc: 'Detects tone, politeness, urgency, and more in real-time.' },
            { icon: ShieldCheck, title: 'Risk Assessment', desc: 'Flags passive-aggressive or unprofessional language before you send.' },
            { icon: Zap, title: 'AI Rewrite', desc: 'Instantly rewrites risky emails while preserving your original intent.' }
          ].map((feature, i) => (
            <div key={i} className="glass-panel bg-white shadow-sm border border-slate-200 rounded-2xl p-6 hover:-translate-y-1 transition-transform">
              <div className="w-12 h-12 rounded-xl bg-slate-50 flex items-center justify-center mb-4 border border-slate-100">
                <feature.icon size={24} className="text-brand-600" />
              </div>
              <h3 className="font-bold text-slate-800 mb-2">{feature.title}</h3>
              <p className="text-sm text-slate-500 leading-relaxed">{feature.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function SparklesIcon(props) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z" />
    </svg>
  )
}
