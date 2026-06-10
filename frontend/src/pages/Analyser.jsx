import { useState } from 'react'
import { Send, RefreshCw, Sparkles, ChevronDown } from 'lucide-react'
import toast from 'react-hot-toast'
import { analyseEmail, rewriteEmail } from '../api/client'
import { useAuth } from '../context/AuthContext'
import ScoreGauge from '../components/analyser/ScoreGauge'
import SignalCards from '../components/analyser/SignalCards'
import RiskFlags from '../components/analyser/RiskFlags'
import RewrittenEmail from '../components/analyser/RewrittenEmail'

const RELATIONSHIPS = [
  { value: 'upward',   label: '⬆️  Writing to my superior' },
  { value: 'peer',     label: '↔️  Writing to a colleague' },
  { value: 'downward', label: '⬇️  Writing to my team' },
]

export default function Analyser() {
  const { user } = useAuth()
  const [emailText,    setEmailText]    = useState('')
  const [senderName,   setSenderName]   = useState(user?.name || '')
  const [receiverName, setReceiverName] = useState('')
  const [relationship, setRelationship] = useState('peer')
  const [loading,      setLoading]      = useState(false)
  const [rewriting,    setRewriting]    = useState(false)
  const [result,       setResult]       = useState(null)
  const [rewriteResult,setRewriteResult]= useState(null)

  const handleAnalyse = async () => {
    if (!emailText.trim()) { toast.error('Please enter an email to analyse.'); return }
    setLoading(true)
    setResult(null)
    setRewriteResult(null)
    try {
      const res = await analyseEmail({ email_text: emailText, sender_name: senderName,
        receiver_name: receiverName, relationship })
      setResult(res.data)
      toast.success('Analysis complete!')
    } catch (e) {
      toast.error(e?.response?.data?.detail || 'Analysis failed. Is the backend running?')
    } finally { setLoading(false) }
  }

  const handleRewrite = async () => {
    if (!result) return
    setRewriting(true)
    try {
      const res = await rewriteEmail({ email_text: emailText, analysis: result.signals,
        sender_name: senderName, receiver_name: receiverName })
      setRewriteResult(res.data)
      toast.success('Email rewritten!')
    } catch (e) {
      toast.error(e?.response?.data?.detail || 'Rewrite failed.')
    } finally { setRewriting(false) }
  }

  const reset = () => { setEmailText(''); setResult(null); setRewriteResult(null) }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 animate-fade-in relative z-10">
      <div className="mb-10 text-center max-w-2xl mx-auto">
        <h1 className="text-4xl font-bold text-slate-900 mb-3">Email Analyser</h1>
        <p className="text-slate-600">Paste your professional email below and get a full communication analysis across 7 intelligent dimensions.</p>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* ── LEFT: Input Panel ── */}
        <div className="flex flex-col gap-6">
          {/* Meta inputs */}
          <div className="glass-panel rounded-2xl p-5 flex flex-col gap-4 bg-white shadow-sm">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-semibold text-slate-500 mb-1 block uppercase tracking-wider">Your Name (optional)</label>
                <input value={senderName} onChange={e => setSenderName(e.target.value)}
                  placeholder="e.g. John Doe"
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-900
                             placeholder-slate-400 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition-all" />
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-500 mb-1 block uppercase tracking-wider">Receiver Name (optional)</label>
                <input value={receiverName} onChange={e => setReceiverName(e.target.value)}
                  placeholder="e.g. Jane Smith"
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-900
                             placeholder-slate-400 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition-all" />
              </div>
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-500 mb-1 block uppercase tracking-wider">Relationship</label>
              <div className="relative">
                <select value={relationship} onChange={e => setRelationship(e.target.value)}
                  className="w-full appearance-none bg-slate-50 border border-slate-200 rounded-lg px-3 py-2
                             text-sm text-slate-900 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition-all pr-8">
                  {RELATIONSHIPS.map(r => <option key={r.value} value={r.value}>{r.label}</option>)}
                </select>
                <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
              </div>
            </div>
          </div>

          {/* Email textarea */}
          <div className="glass-panel rounded-2xl overflow-hidden flex-1 flex flex-col group focus-within:border-brand-500 focus-within:shadow-md transition-all bg-white shadow-sm">
            <div className="flex items-center justify-between px-5 py-3 border-b border-slate-100 bg-slate-50/50">
              <span className="text-xs text-slate-500 font-semibold uppercase tracking-wider">Email Content</span>
              {emailText && (
                <button onClick={reset} className="text-xs text-slate-500 hover:text-slate-700 font-medium transition-colors">
                  Clear
                </button>
              )}
            </div>
            <textarea
              value={emailText}
              onChange={e => setEmailText(e.target.value)}
              placeholder="Paste your professional email here...&#10;&#10;e.g. 'As per my last email, I still haven't received the report. Please ensure this is sent by EOD or I will have to escalate.'"
              className="flex-1 w-full bg-transparent p-5 text-sm text-slate-700 placeholder-slate-400 resize-none
                         focus:outline-none leading-relaxed"
              rows={14}
            />
            <div className="px-5 py-4 border-t border-slate-100 bg-slate-50/50 flex items-center justify-between">
              <span className="text-xs font-medium text-slate-500">{emailText.length} chars</span>
              <button onClick={handleAnalyse} disabled={loading || !emailText.trim()}
                className="btn-primary py-2.5 px-6 text-sm">
                {loading ? <><RefreshCw size={16} className="animate-spin" /> Analysing…</> : <><Send size={16} /> Analyse</>}
              </button>
            </div>
          </div>
        </div>

        {/* ── RIGHT: Results Panel ── */}
        <div className="flex flex-col gap-6">
          {!result && !loading && (
            <div className="glass-panel bg-white rounded-2xl flex-1 flex items-center justify-center min-h-64 border-dashed border-slate-300">
              <div className="text-center px-8">
                <div className="text-4xl mb-4 opacity-50">📧</div>
                <p className="text-slate-600 font-medium">Analysis results will appear here</p>
                <p className="text-slate-400 text-sm mt-1">Paste an email on the left and click Analyse</p>
              </div>
            </div>
          )}

          {loading && (
            <div className="glass-panel bg-white rounded-2xl flex-1 flex items-center justify-center min-h-64 border-brand-200 shadow-glow-primary">
              <div className="text-center">
                <RefreshCw size={28} className="animate-spin text-brand-500 mx-auto mb-3" />
                <p className="text-slate-500 font-medium text-sm">Running 7 detection models…</p>
              </div>
            </div>
          )}

          {result && !loading && (
            <div className="flex flex-col gap-5 animate-slide-up">
              {/* Score + Overview */}
              <div className="glass-panel bg-white rounded-2xl p-6 relative overflow-hidden shadow-sm">
                <div className="absolute top-0 right-0 w-32 h-32 bg-brand-50 rounded-full blur-[40px]" />
                <div className="flex items-center gap-8 relative z-10">
                  <ScoreGauge score={result.score?.score || 0} />
                  <div className="flex-1">
                    <h3 className="text-sm font-bold text-slate-800 mb-1 uppercase tracking-wider">Professionalism Score</h3>
                    <p className="text-sm text-slate-500 leading-relaxed">
                      Based on 7 parallel analysis models including tone, politeness,
                      passive-aggression, sarcasm, urgency, intent and power dynamic detection.
                    </p>
                    <button onClick={handleRewrite} disabled={rewriting}
                      className="mt-4 flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold
                                 bg-brand-50 text-brand-700 border border-brand-200
                                 hover:bg-brand-100 transition-all disabled:opacity-50">
                      {rewriting
                        ? <><RefreshCw size={14} className="animate-spin" /> Rewriting…</>
                        : <><Sparkles size={14} /> Rewrite with AI</>}
                    </button>
                  </div>
                </div>
              </div>

              {/* Signal Cards */}
              <div className="glass-panel bg-white shadow-sm rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-3">
                  <p className="text-sm font-bold text-slate-800 uppercase tracking-wider">Detection Signals</p>
                  <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2 py-1 rounded-full">7 Models</span>
                </div>
                <SignalCards signals={result.signals} />
              </div>

              {/* Risk Flags */}
              <div className="glass-panel bg-white shadow-sm rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-3">
                  <p className="text-sm font-bold text-slate-800 uppercase tracking-wider">Risk Assessment</p>
                  <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2 py-1 rounded-full">{result.risk_flags?.length || 0} Flags</span>
                </div>
                <RiskFlags flags={result.risk_flags} />
              </div>
            </div>
          )}

          {/* Rewritten email */}
          {rewriteResult && (
            <div className="animate-fade-in">
              <RewrittenEmail result={rewriteResult} />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
