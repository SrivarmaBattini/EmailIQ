import { Link, useLocation, useNavigate } from 'react-router-dom'
import { Mail, BarChart3, MessageSquare, LayoutDashboard, LogIn, LogOut, Bot } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'

const links = [
  { to: '/analyse',   label: 'Analyser',  icon: MessageSquare },
  { to: '/thread',    label: 'Thread',    icon: BarChart3 },
  { to: '/coach',     label: 'Assistant',     icon: Bot },
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
]

export default function Navbar() {
  const { pathname } = useLocation()
  const { user, logout } = useAuth()
  const nav = useNavigate()

  return (
    <nav className="sticky top-0 z-50 glass-navbar">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 font-bold text-xl group">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center gradient-bg shadow-glow-primary transition-transform group-hover:scale-105">
            <Mail size={16} color="white" />
          </div>
          <span className="text-slate-800 tracking-tight font-extrabold">Email<span className="gradient-text">IQ</span></span>
        </Link>

        <div className="flex items-center gap-6">
          {user && (
            <div className="hidden md:flex items-center gap-1 bg-slate-100 p-1 rounded-xl border border-slate-200 shadow-sm">
              {links.map(({ to, label, icon: Icon }) => {
                const isActive = pathname === to
                return (
                  <Link key={to} to={to}
                    className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-semibold transition-all duration-300
                      ${isActive
                        ? 'bg-white text-brand-600 shadow-sm'
                        : 'text-slate-500 hover:text-slate-700 hover:bg-slate-200/50'}`}>
                    <Icon size={15} className={isActive ? 'text-brand-500' : ''} />
                    <span>{label}</span>
                  </Link>
                )
              })}
            </div>
          )}

          <div className="flex items-center gap-3 border-l border-slate-200 pl-6">
            {user ? (
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2">
                  <img src={user.avatar} alt={user.name} className="w-8 h-8 rounded-full border border-slate-200 shadow-sm" />
                  <span className="text-sm font-semibold text-slate-700 hidden sm:block">{user.name}</span>
                </div>
                <button onClick={logout} className="p-2 text-slate-400 hover:text-red-500 transition-colors rounded-lg hover:bg-red-50">
                  <LogOut size={16} />
                </button>
              </div>
            ) : (
              <button onClick={() => nav('/auth')} className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold bg-white text-slate-700 border border-slate-200 hover:bg-slate-50 shadow-sm transition-all">
                <LogIn size={15} />
                <span className="hidden sm:block">Sign In</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
