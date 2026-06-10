import { scoreColor } from '../../utils/scoreColor'

export default function ScoreGauge({ score }) {
  const { text, label } = scoreColor(score)
  const radius = 52
  const circ   = 2 * Math.PI * radius
  const offset = circ - (score / 100) * circ

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative w-36 h-36">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
          <circle cx="60" cy="60" r={radius}
            fill="none" stroke="#f1f5f9" strokeWidth="10" />
          <circle cx="60" cy="60" r={radius}
            fill="none" stroke={text} strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={circ}
            strokeDashoffset={offset}
            className="score-ring drop-shadow-md"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-4xl font-black" style={{ color: text }}>{score}</span>
          <span className="text-xs font-bold text-slate-400">/ 100</span>
        </div>
      </div>
      <span className="px-3 py-1 rounded-full text-xs font-semibold"
            style={{ background: `${text}20`, color: text, border: `1px solid ${text}40` }}>
        {label}
      </span>
    </div>
  )
}
