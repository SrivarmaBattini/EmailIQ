import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Loader2, Copy, Check } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

export default function Coach() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hello! I am your AI Assistant. How can I help you draft or refine an email today?"
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [copiedId, setCopiedId] = useState(null)
  const messagesEndRef = useRef(null)

  const handleCopy = (text, idx) => {
    navigator.clipboard.writeText(text)
    setCopiedId(idx)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async (e) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage = { role: 'user', content: input.trim() }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: [...messages, userMessage] })
      })

      if (!response.ok) throw new Error('Failed to fetch response')
      
      const data = await response.json()
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }])
    } catch (error) {
      console.error(error)
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please ensure the backend is running.' }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 h-[calc(100vh-80px)] flex flex-col">
      <div className="mb-6">
        <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">
          AI Assistant
        </h1>
        <p className="text-gray-500 mt-2">Brainstorm, outline, and draft professional emails with AI.</p>
      </div>

      <div className="flex-1 bg-white/50 backdrop-blur-xl border border-white/20 shadow-xl rounded-2xl flex flex-col overflow-hidden relative z-10">
        
        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
              
              <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${
                msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-indigo-100 text-indigo-600'
              }`}>
                {msg.role === 'user' ? <User size={20} /> : <Bot size={20} />}
              </div>

              <div className={`max-w-[75%] rounded-2xl px-5 py-4 relative group ${
                msg.role === 'user' 
                  ? 'bg-blue-600 text-white rounded-tr-none' 
                  : 'bg-white border border-gray-100 shadow-sm rounded-tl-none text-gray-800'
              }`}>
                {msg.role === 'assistant' && (
                  <button 
                    onClick={() => handleCopy(msg.content, idx)}
                    className="absolute top-2 right-2 p-1.5 rounded-lg bg-gray-50 text-gray-400 hover:text-gray-600 hover:bg-gray-100 opacity-0 group-hover:opacity-100 transition-all"
                    title="Copy to clipboard"
                  >
                    {copiedId === idx ? <Check size={14} className="text-green-500" /> : <Copy size={14} />}
                  </button>
                )}
                
                {msg.role === 'assistant' ? (
                  <div className="prose prose-sm max-w-none text-gray-800 prose-p:leading-relaxed prose-pre:bg-gray-50 prose-pre:text-gray-800 prose-pre:border prose-pre:border-gray-200">
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                ) : (
                  <div className="whitespace-pre-wrap leading-relaxed">{msg.content}</div>
                )}
              </div>

            </div>
          ))}
          {isLoading && (
            <div className="flex gap-4">
              <div className="w-10 h-10 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center shrink-0">
                <Bot size={20} />
              </div>
              <div className="bg-white border border-gray-100 shadow-sm rounded-2xl rounded-tl-none px-5 py-4 flex items-center gap-2">
                <Loader2 className="w-5 h-5 animate-spin text-indigo-600" />
                <span className="text-gray-500 text-sm">Thinking...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-white/80 border-t border-gray-100 backdrop-blur-md">
          <form onSubmit={handleSend} className="relative flex items-center">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask the AI Assistant to draft an email..."
              className="w-full pl-6 pr-14 py-4 rounded-full border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 bg-white shadow-sm transition-all text-gray-700"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="absolute right-2 p-3 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-50 disabled:hover:bg-blue-600 transition-colors"
            >
              <Send size={18} />
            </button>
          </form>
        </div>

      </div>

      {/* Decorative Elements */}
      <div className="fixed top-20 right-0 w-96 h-96 bg-blue-400/10 rounded-full blur-3xl -z-10 animate-pulse"></div>
      <div className="fixed bottom-0 left-0 w-96 h-96 bg-purple-400/10 rounded-full blur-3xl -z-10 animate-pulse" style={{animationDelay: '1s'}}></div>
    </div>
  )
}
