import { motion } from 'framer-motion'

export function HudPanel({ title, children }) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="jarvis-panel"
    >
      <h3 className="mb-3 text-sm uppercase tracking-[0.2em] text-jarvisNeon">{title}</h3>
      {children}
    </motion.section>
  )
}
