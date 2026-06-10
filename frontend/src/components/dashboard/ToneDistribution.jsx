import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts'

const COLORS = {
  professional: '#22c55e',
  aggressive:   '#ef4444',
  frustrated:   '#f97316',
  unknown:      '#475569',
}

export default function ToneDistribution({ toneDistribution }) {
  const data = Object.entries(toneDistribution || {}).map(([name, value]) => ({ name, value }))
  if (!data.length) return <p className="text-slate-500 text-sm text-center py-8">No data yet</p>

  return (
    <ResponsiveContainer width="100%" height={180}>
      <PieChart>
        <Pie data={data} cx="50%" cy="50%" innerRadius={45} outerRadius={70}
             paddingAngle={3} dataKey="value">
          {data.map((entry) => (
            <Cell key={entry.name} fill={COLORS[entry.name] || '#6366f1'} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: 12, boxShadow: '0 8px 30px rgba(0,0,0,0.1)' }}
          itemStyle={{ color: '#334155', fontWeight: 600 }}
        />
        <Legend iconType="circle" iconSize={8}
                formatter={v => <span style={{ color: '#64748b', fontSize: 12, fontWeight: 600, textTransform: 'capitalize' }}>{v}</span>} />
      </PieChart>
    </ResponsiveContainer>
  )
}
