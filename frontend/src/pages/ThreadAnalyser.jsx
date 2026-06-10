import { useState } from 'react'
import { Send, RefreshCw, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import toast from 'react-hot-toast'
import { analyseThread } from '../api/client'
import ToneDriftChart from '../components/thread/ToneDriftChart'
import { scoreColor } from '../utils/scoreColor'

const DRIFT_ICONS = { improving: TrendingUp, deteriorating: TrendingDown, stable: Minus }
const DRIFT_COLORS = { improving: '#22c55e', deteriorating: '#ef4444', stable: '#94a3b8' }

export default function ThreadAnalyser() {
  const [threadText, setThreadText] = useState('')
  const [loading,    setLoading]    = useState(false)
  const [result,     setResult]     = useState(null)

  const handleAnalyse = async () => {
    if (!threadText.trim()) { toast.error('Please paste an email thread.'); return }
    setLoading(true); setResult(null)
    try {
      const res = await analyseThread({ thread_text: threadText })
      setResult(res.data)
      toast.success(`Analysed ${res.data.emails?.length} emails in thread`)
    } catch (e) {
      toast.error(e?.response?.data?.detail || 'Thread analysis failed.')
    } finally { setLoading(false) }
  }

  const drift     = result?.drift
  const DriftIcon = drift ? DRIFT_ICONS[drift.direction] || Minus : null
  const driftColor= drift ? DRIFT_COLORS[drift.direction] || '#94a3b8' : '#94a3b8'

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-100 mb-2">Thread Analyser</h1>
        <p className="text-slate-500 text-sm">Paste a full email thread to detect tone drift across the conversation.</p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Input */}
        <div className="glass-panel rounded-2xl overflow-hidden flex flex-col group focus-within:border-indigo-500/50 transition-colors">
          <div className="px-5 py-3 border-b border-white/5 bg-dark-900/40 flex items-center justify-between">
            <span className="text-xs text-slate-500 font-medium">Email Thread</span>
            {threadText && (
              <button onClick={() => setThreadText('')} className="text-xs text-slate-600 hover:text-slate-400 transition-colors">
                Clear
              </button>
            )}
          </div>
          <textarea value={threadText} onChange={e => setThreadText(e.target.value)}
            placeholder={"Paste your full email thread here...\n\nThe system will automatically split each email and analyse them individually.\n\nSupports Gmail, Outlook and plain text formats."}
            className="flex-1 w-full bg-transparent p-5 text-sm text-slate-700 placeholder-slate-400 resize-none focus:outline-none leading-relaxed"
            rows={16} />
          <div className="px-5 py-4 border-t border-slate-100 bg-slate-50/50 flex justify-end">
            <button onClick={handleAnalyse} disabled={loading || !threadText.trim()}
              className="btn-primary py-2.5 px-6 text-sm">
              {loading ? <><RefreshCw size={16} className="animate-spin" /> Analysing…</> : <><Send size={16} /> Analyse Thread</>}
            </button>
          </div>
        </div>

        {/* Results */}
        <div className="flex flex-col gap-6">
          {!result && !loading && (
            <div className="glass-panel bg-white shadow-sm rounded-2xl flex items-center justify-center min-h-64 border-dashed border-slate-300">
              <div className="text-center px-8">
                <div className="text-4xl mb-4 opacity-50">🧵</div>
                <p className="text-slate-600 font-medium">Thread analysis will appear here</p>
              </div>
            </div>
          )}

          {loading && (
            <div className="glass-panel bg-white shadow-sm rounded-2xl flex items-center justify-center min-h-64 border-brand-200 shadow-glow-primary">
              <div className="text-center">
                <RefreshCw size={28} className="animate-spin text-brand-500 mx-auto mb-3" />
                <p className="text-slate-500 font-medium text-sm">Analysing each email in thread…</p>
              </div>
            </div>
          )}

          {result && !loading && (
            <div className="flex flex-col gap-6 animate-slide-up">
              {/* Drift summary */}
              {drift && (
                <div className="glass-panel bg-white shadow-sm rounded-2xl p-6 relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-brand-50 rounded-full blur-[40px]" />
                  <div className="flex items-center gap-4 mb-4 relative z-10">
                    <div className="p-2 rounded-lg" style={{ background: `${driftColor}15` }}>
                      {DriftIcon && <DriftIcon size={24} style={{ color: driftColor }} />}
                    </div>
                    <div>
                      <p className="text-sm font-bold uppercase tracking-wider" style={{ color: driftColor }}>
                        Tone is {drift.direction}
                      </p>
                      <p className="text-sm font-medium text-slate-500">{drift.summary}</p>
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-3 mt-4 relative z-10">
                    {[
                      { label: 'Start avg', value: drift.avg_start },
                      { label: 'End avg',   value: drift.avg_end },
                      { label: 'Worst email', value: `#${drift.worst_index} (${drift.worst_score})` },
                    ].map(({ label, value }) => (
                      <div key={label} className="bg-slate-50 rounded-xl p-3 text-center border border-slate-100">
                        <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1">{label}</p>
                        <p className="text-lg font-black text-slate-800">{value}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Chart */}
              {result.emails?.length > 0 && (
                <div className="glass-panel bg-white shadow-sm rounded-2xl p-6">
                  <p className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-4 border-b border-slate-100 pb-3">Score per Email</p>
                  <ToneDriftChart emails={result.emails} />
                  <div className="flex items-center gap-4 mt-4 text-xs text-slate-500 font-semibold uppercase tracking-wider">
                    <span className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-yellow-500"></div> Acceptable (65)</span>
                    <span className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-red-500"></div> Poor (40)</span>
                  </div>
                </div>
              )}

              {/* Email list */}
              <div className="glass-panel bg-white shadow-sm rounded-2xl p-6">
                <p className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-4 border-b border-slate-100 pb-3">Individual Email Scores</p>
                <div className="flex flex-col gap-3">
                  {result.emails?.map(email => {
                    const { text, bg, border } = scoreColor(email.score)
                    return (
                      <div key={email.index}
                           className="flex items-center gap-4 p-4 rounded-xl border hover:shadow-soft transition-shadow bg-white"
                           style={{ borderColor: text }}>
                        <span className="text-xs font-bold text-slate-500 w-6">#{email.index}</span>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-slate-700 truncate">{email.text?.slice(0, 80)}…</p>
                          <div className="flex items-center gap-2 mt-1">
                            {email.signals?.tone && (
                              <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded uppercase tracking-wider">{email.signals.tone}</span>
                            )}
                            {email.signals?.pa === 'passive_aggressive' && (
                              <span className="text-xs font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">PA Detected</span>
                            )}
                          </div>
                        </div>
                        <div className="w-12 h-12 rounded-full flex flex-col items-center justify-center shadow-sm"
                             style={{ background: `${text}15`, border: `1px solid ${text}30` }}>
                          <span className="text-sm font-black" style={{ color: text }}>{email.score}</span>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
