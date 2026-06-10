import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function ScoreHistory({ history }) {
  const data = history.map((h, i) => ({
    i: i + 1,
    score: h.score,
    date: h.timestamp?.slice(0, 10) || '',
    preview: h.preview || '',
  }))

  return (
    <ResponsiveContainer width="100%" height={180}>
      <LineChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="i" stroke="#94a3b8" tick={{ fontSize: 11, fontWeight: 500 }} />
        <YAxis domain={[0, 100]} stroke="#94a3b8" tick={{ fontSize: 11, fontWeight: 500 }} />
        <Tooltip
          contentStyle={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: 12, boxShadow: '0 8px 30px rgba(0,0,0,0.1)' }}
          labelStyle={{ color: '#64748b', fontWeight: 600, marginBottom: 4 }}
          itemStyle={{ color: '#6366f1', fontWeight: 700, fontSize: 16 }}
        />
        <Line type="monotone" dataKey="score" stroke="url(#colorScore)"
              strokeWidth={3} dot={{ r: 4, fill: '#ffffff', strokeWidth: 2 }} activeDot={{ r: 6, fill: '#8b5cf6', strokeWidth: 0, boxShadow: '0 0 10px #8b5cf6' }} />
        <defs>
          <linearGradient id="colorScore" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#8b5cf6" />
            <stop offset="100%" stopColor="#6366f1" />
          </linearGradient>
        </defs>
      </LineChart>
    </ResponsiveContainer>
  )
}
