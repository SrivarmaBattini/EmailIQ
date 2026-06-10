export function scoreColor(score) {
  if (score >= 85) return { text: '#22c55e', bg: 'rgba(34,197,94,0.1)',  border: 'rgba(34,197,94,0.3)',  label: 'Excellent' }
  if (score >= 65) return { text: '#eab308', bg: 'rgba(234,179,8,0.1)',  border: 'rgba(234,179,8,0.3)',  label: 'Acceptable' }
  if (score >= 40) return { text: '#f97316', bg: 'rgba(249,115,22,0.1)', border: 'rgba(249,115,22,0.3)', label: 'Needs Improvement' }
  return               { text: '#ef4444', bg: 'rgba(239,68,68,0.1)',  border: 'rgba(239,68,68,0.3)',  label: 'Poor' }
}

export function confidenceBadge(conf) {
  const pct = Math.round(conf * 100)
  if (pct >= 80) return { color: '#22c55e', label: `${pct}%` }
  if (pct >= 60) return { color: '#eab308', label: `${pct}%` }
  return               { color: '#94a3b8', label: `${pct}%` }
}

export const SIGNAL_META = {
  politeness: { icon: '🤝', label: 'Politeness',        positive: 'polite',        negative: 'impolite' },
  tone:       { icon: '🎙️', label: 'Tone',              positive: 'professional',   negative: 'aggressive' },
  intent:     { icon: '🎯', label: 'Intent',             positive: null,             negative: null },
  pa:         { icon: '😶', label: 'Passive-Aggression', positive: 'neutral',        negative: 'passive_aggressive' },
  sarcasm:    { icon: '😏', label: 'Sarcasm',            positive: 'neutral',        negative: 'sarcastic' },
  urgency:    { icon: '⏱️', label: 'Urgency',            positive: 'low',            negative: 'high' },
  power:      { icon: '🏢', label: 'Power Dynamic',      positive: null,             negative: null },
}
