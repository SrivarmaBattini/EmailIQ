import { SIGNAL_META, confidenceBadge } from '../../utils/scoreColor'

function formatLabel(str) {
  return str?.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) || '—'
}

function signalColor(task, label) {
  const meta = SIGNAL_META[task]
  if (!meta) return '#94a3b8'
  if (meta.negative && label === meta.negative) return '#ef4444'
  if (meta.positive && label === meta.positive) return '#22c55e'
  return '#94a3b8'
}

export default function SignalCards({ signals }) {
  if (!signals) return null

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
      {Object.entries(SIGNAL_META).map(([task, meta]) => {
        const result = signals[task]
        if (!result) return null
        const label = result.label || 'unknown'
        const conf  = result.confidence || 0
        const color = signalColor(task, label)
        const badge = confidenceBadge(conf)

        return (
          <div key={task}
               className="bg-slate-50 border border-slate-100 rounded-xl p-4 flex flex-col gap-3 hover:border-brand-300 hover:shadow-soft transition-all duration-300 hover:-translate-y-1 group">
            <div className="flex items-center justify-between">
              <span className="text-xl group-hover:scale-110 transition-transform">{meta.icon}</span>
              <span className="text-xs font-bold px-2.5 py-1 rounded-full uppercase tracking-wider"
                    style={{ color: badge.color, background: `${badge.color}15` }}>
                {badge.label}
              </span>
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-500 mb-1 uppercase tracking-wider">{meta.label}</p>
              <p className="text-sm font-bold text-slate-900">
                {formatLabel(label)}
              </p>
            </div>
          </div>
        )
      })}
    </div>
  )
}
