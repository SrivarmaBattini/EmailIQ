import { useState } from 'react'
import { Copy, Check, Sparkles, AlertCircle, Database } from 'lucide-react'
import toast from 'react-hot-toast'

export default function RewrittenEmail({ result }) {
  const [copied, setCopied] = useState(false)

  if (!result) return null

  const copy = () => {
    navigator.clipboard.writeText(result.rewritten_email)
    setCopied(true)
    toast.success('Copied to clipboard!')
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="glass-panel rounded-2xl overflow-hidden mt-6 animate-slide-up bg-white shadow-sm border-slate-200">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100 bg-slate-50">
        <div className="flex items-center gap-3">
          <div className="p-1.5 bg-brand-50 rounded-lg">
            <Sparkles size={16} className="text-brand-600" />
          </div>
          <span className="text-sm font-bold text-slate-800 uppercase tracking-wider">Rewritten Email</span>
          {result.intent_preserved && (
            <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 font-bold border border-emerald-200">
              Intent Preserved
            </span>
          )}
          {result.rag_used && (
            <span className="flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full bg-blue-50 text-blue-700 font-bold border border-blue-200">
              <Database size={12} />
              RAG Enhanced
            </span>
          )}
        </div>
        <button onClick={copy}
          className="flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all
                     bg-white text-slate-700 border border-slate-200 hover:bg-slate-50 hover:text-brand-600 shadow-sm">
          {copied ? <Check size={14} /> : <Copy size={14} />}
          {copied ? 'Copied!' : 'Copy Text'}
        </button>
      </div>

      {/* Subject line */}
      {result.subject_line && (
        <div className="px-5 py-3 border-b border-slate-100 bg-white">
          <span className="text-xs text-slate-500 uppercase tracking-wider font-semibold mr-2">Subject:</span>
          <span className="text-sm text-slate-800 font-medium">{result.subject_line}</span>
        </div>
      )}

      {/* Body */}
      <div className="p-6 bg-white">
        <p className="text-base text-slate-700 leading-relaxed whitespace-pre-wrap">
          {result.rewritten_email}
        </p>
      </div>

      {/* Footer stats */}
      <div className="px-5 py-3 border-t border-slate-100 bg-slate-50 flex items-center gap-6 flex-wrap">
        <span className="text-xs font-semibold text-slate-500 flex items-center gap-1.5 uppercase tracking-wider">
          Similarity: <span className="text-slate-700 font-mono bg-white px-2 py-0.5 rounded border border-slate-200">{(result.similarity * 100).toFixed(0)}%</span>
        </span>
        {result.issues_fixed?.length > 0 && (
          <span className="text-xs font-semibold text-slate-500 flex items-center gap-1.5 uppercase tracking-wider">
            Fixed: <span className="text-brand-600 font-bold">{result.issues_fixed.join(', ')}</span>
          </span>
        )}
        {result.rag_used && (
          <span className="text-xs font-semibold text-blue-600 flex items-center gap-1.5">
            ✦ Rewritten using similar email examples
          </span>
        )}
        {result.warning && (
          <div className="flex items-center gap-1.5 text-xs text-amber-700 font-bold bg-amber-50 px-3 py-1 rounded-full border border-amber-200">
            <AlertCircle size={12} />
            {result.warning}
          </div>
        )}
      </div>
    </div>
  )
}
