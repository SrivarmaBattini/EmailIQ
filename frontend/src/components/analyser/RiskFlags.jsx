import { AlertTriangle, AlertOctagon, Info } from 'lucide-react'

const ICONS = { HIGH: AlertOctagon, MEDIUM: AlertTriangle, LOW: Info }

export default function RiskFlags({ flags }) {
  if (!flags || flags.length === 0) {
    return (
      <div className="flex items-center gap-3 p-4 rounded-xl border border-emerald-200 bg-emerald-50 shadow-sm">
        <span className="text-emerald-500 text-lg">✓</span>
        <span className="text-emerald-700 text-sm font-bold">No communication risks detected</span>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-3">
      {flags.map(flag => {
        const Icon = ICONS[flag.level] || Info
        return (
          <div key={flag.id}
               className="flex items-start gap-3 p-4 rounded-xl border bg-white hover:shadow-soft transition-shadow"
               style={{ borderColor: `${flag.color}30` }}>
            <div className="p-1.5 rounded-lg" style={{ background: `${flag.color}15` }}>
              <Icon size={18} style={{ color: flag.color }} />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-sm font-bold" style={{ color: flag.color }}>
                  {flag.title}
                </span>
                <span className="text-xs px-2 py-0.5 rounded-full font-bold tracking-wider uppercase"
                      style={{ background: `${flag.color}15`, color: flag.color }}>
                  {flag.level}
                </span>
              </div>
              <p className="text-sm text-slate-600 font-medium leading-relaxed">{flag.message}</p>
            </div>
          </div>
        )
      })}
    </div>
  )
}
