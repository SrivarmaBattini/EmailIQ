import { useState, useEffect } from 'react'
import { RefreshCw, Mail, AlertTriangle, TrendingUp, Star, LogIn } from 'lucide-react'
import { Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import { getSenderProfile } from '../api/client'
import { useAuth } from '../context/AuthContext'
import ScoreHistory from '../components/dashboard/ScoreHistory'
import ToneDistribution from '../components/dashboard/ToneDistribution'
import { scoreColor } from '../utils/scoreColor'

export default function Dashboard() {
  const { user } = useAuth()
  const [loading, setLoading] = useState(false)
  const [profile, setProfile] = useState(null)

  useEffect(() => {
    if (user?.name) {
      const fetchProfile = async () => {
        setLoading(true)
        try {
          const res = await getSenderProfile(user.name)
          setProfile(res.data)
        } catch (e) {
          toast.error('Could not fetch your profile data.')
        } finally {
          setLoading(false)
        }
      }
      fetchProfile()
    }
  }, [user])

  const avgColor = profile ? scoreColor(profile.average_score || 0) : null

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 animate-fade-in relative z-10">
      <div className="mb-10 text-center max-w-2xl mx-auto">
        <h1 className="text-4xl font-bold text-slate-900 mb-3">Sender Dashboard</h1>
        <p className="text-slate-600 mb-4">Search for a sender's communication history, track their professionalism score, and view tone distribution.</p>
      </div>

      {/* Not Logged In */}
      {!user && (
        <div className="glass-panel bg-white rounded-3xl flex items-center justify-center min-h-[400px] border-dashed border-slate-300 shadow-sm">
          <div className="text-center px-8">
            <div className="text-6xl mb-6 opacity-50">🔒</div>
            <p className="text-slate-700 text-lg font-bold">Please sign in to view your dashboard</p>
            <p className="text-slate-500 text-sm mt-2 max-w-md mx-auto mb-6">
              Your dashboard will automatically track and display your communication profile.
            </p>
            <Link to="/auth" className="btn-primary inline-flex items-center gap-2 px-6 py-3">
              <LogIn size={18} /> Sign In
            </Link>
          </div>
        </div>
      )}

      {/* Loading */}
      {user && loading && (
        <div className="glass-panel bg-white rounded-3xl flex items-center justify-center min-h-[400px] border-slate-200 shadow-sm">
          <div className="text-center">
            <RefreshCw size={32} className="animate-spin text-brand-500 mx-auto mb-4" />
            <p className="text-slate-500 font-medium">Loading your profile...</p>
          </div>
        </div>
      )}

      {/* No profile data yet */}
      {user && !profile && !loading && (
        <div className="glass-panel bg-white rounded-3xl flex items-center justify-center min-h-[400px] border-dashed border-slate-300 shadow-sm">
          <div className="text-center px-8">
            <div className="text-6xl mb-6 opacity-50">📊</div>
            <p className="text-slate-700 text-lg font-bold">No emails analysed yet, {user.name.split(' ')[0]}</p>
            <p className="text-slate-500 text-sm mt-2 max-w-md mx-auto mb-6">
              Head over to the Analyser tab to start building your communication profile.
            </p>
            <Link to="/analyse" className="btn-primary inline-flex px-6 py-3">
              Go to Analyser
            </Link>
          </div>
        </div>
      )}

      {/* Profile loaded */}
      {profile && !loading && (
        <div className="flex flex-col gap-6 animate-slide-up">
          {/* Stats row */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
            {[
              { icon: Mail,          label: 'Total Emails',    value: profile.total_emails,  color: '#6366f1' },
              { icon: Star,          label: 'Avg Score',       value: profile.average_score, color: avgColor?.text || '#94a3b8' },
              { icon: AlertTriangle, label: 'Flagged Emails',  value: profile.flagged_count, color: '#f97316' },
              { icon: TrendingUp,    label: 'Profile',         value: profile.average_score >= 65 ? 'Good' : 'At Risk', color: profile.average_score >= 65 ? '#22c55e' : '#ef4444' },
            ].map(({ icon: Icon, label, value, color }) => (
              <div key={label} className="glass-panel bg-white shadow-sm rounded-2xl p-6 group hover:-translate-y-1 transition-all duration-300">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-2 rounded-lg" style={{ background: `${color}15` }}>
                    <Icon size={18} style={{ color }} />
                  </div>
                </div>
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1 block">{label}</span>
                <p className="text-3xl font-black text-slate-800" style={{ color: label === 'Total Emails' ? '#1e293b' : color }}>{value}</p>
              </div>
            ))}
          </div>

          {/* Charts row */}
          <div className="grid md:grid-cols-2 gap-6">
            <div className="glass-panel bg-white shadow-sm rounded-2xl p-6">
              <p className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-4 border-b border-slate-100 pb-3">Score History (last 30)</p>
              {profile.score_history?.length > 0
                ? <ScoreHistory history={profile.score_history} />
                : <p className="text-slate-500 text-xs text-center py-8">No history available</p>
              }
            </div>

            <div className="glass-panel bg-white shadow-sm rounded-2xl p-6">
              <p className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-4 border-b border-slate-100 pb-3">Tone Distribution</p>
              <ToneDistribution toneDistribution={profile.tone_distribution} />
            </div>
          </div>

          {/* Recent emails */}
          {profile.score_history?.length > 0 && (
            <div className="glass-panel bg-white shadow-sm rounded-2xl p-6">
              <p className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-4 border-b border-slate-100 pb-3">Recent Emails</p>
              <div className="flex flex-col gap-3">
                {profile.score_history.slice(-5).reverse().map((h, i) => {
                  const { text } = scoreColor(h.score)
                  return (
                    <div key={i} className="flex items-center gap-4 p-4 rounded-xl border bg-white hover:shadow-soft transition-shadow"
                         style={{ borderColor: text }}>
                      <div className="w-12 h-12 rounded-full flex flex-col items-center justify-center shadow-sm"
                           style={{ background: `${text}15`, border: `1px solid ${text}30` }}>
                        <span className="text-sm font-black" style={{ color: text }}>{h.score}</span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-slate-700 truncate">{h.preview || 'No preview available'}…</p>
                        <p className="text-xs font-semibold text-slate-400 mt-1 uppercase tracking-wider">{new Date(h.timestamp).toLocaleString()}</p>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
