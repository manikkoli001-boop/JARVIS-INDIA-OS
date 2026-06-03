import { NavLink, Outlet } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useSocketEvents } from '../hooks/useSocketEvents'
import { NotificationTray } from '../components/NotificationTray'

const navItems = [
  { to: '/', label: 'Dashboard' },
  { to: '/', label: 'AI Chat' },
  { to: '/', label: 'Voice' },
  { to: '/', label: 'Terminal' },
]

export function AppLayout() {
  useSocketEvents()

  return (
    <div className="min-h-screen bg-jarvisBg text-white">
      <div className="jarvis-grid absolute inset-0 opacity-25" />
      <div className="relative z-10 mx-auto grid max-w-[1500px] grid-cols-1 gap-4 p-4 lg:grid-cols-[250px_1fr]">
        <motion.aside
          initial={{ x: -40, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          className="jarvis-panel h-fit"
        >
          <h1 className="mb-4 text-xl font-bold tracking-[0.18em] text-jarvisNeon">JARVIS INDIA OS</h1>
          <nav className="space-y-2">
            {navItems.map((item) => (
              <NavLink key={`${item.label}-${item.to}`} to={item.to} className="jarvis-link block">
                {item.label}
              </NavLink>
            ))}
          </nav>
        </motion.aside>
        <main className="space-y-4">
          <Outlet />
        </main>
      </div>
      <NotificationTray />
    </div>
  )
}
