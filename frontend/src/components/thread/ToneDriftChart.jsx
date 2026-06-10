import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'
import { scoreColor } from '../../utils/scoreColor'

const CustomDot = (props) => {
  const { cx, cy, payload } = props
  const { text } = scoreColor(payload.score)
  return <circle cx={cx} cy={cy} r={5} fill={text} stroke="none" />
}

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  const { text, label } = scoreColor(d.score)
  return (
    <div className="glass-panel rounded-xl p-4 text-xs shadow-glass border-white/10">
      <p className="text-slate-400 mb-2 font-medium uppercase tracking-wide">Email #{d.index}</p>
      <div className="flex items-end gap-2">
        <p className="font-black text-2xl leading-none" style={{ color: text }}>{d.score}</p>
        <p className="font-semibold pb-0.5" style={{ color: text }}>{label}</p>
      </div>
    </div>
  )
}

export default function ToneDriftChart({ emails }) {
  const data = emails.map(e => ({ index: e.index, score: e.score, grade: e.grade }))
  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="index" stroke="#94a3b8" tick={{ fontSize: 11, fontWeight: 500 }}
               tickFormatter={v => `#${v}`} />
        <YAxis domain={[0, 100]} stroke="#94a3b8" tick={{ fontSize: 11, fontWeight: 500 }} />
        <Tooltip content={<CustomTooltip />} />
        <ReferenceLine y={65} stroke="#eab308" strokeDasharray="4 4" strokeOpacity={0.8} />
        <ReferenceLine y={40} stroke="#ef4444" strokeDasharray="4 4" strokeOpacity={0.8} />
        <Line type="monotone" dataKey="score" stroke="#8b5cf6" strokeWidth={3}
              dot={<CustomDot />} activeDot={{ r: 7, fill: '#8b5cf6', strokeWidth: 0, boxShadow: '0 0 10px #8b5cf6' }} />
      </LineChart>
    </ResponsiveContainer>
  )
}
