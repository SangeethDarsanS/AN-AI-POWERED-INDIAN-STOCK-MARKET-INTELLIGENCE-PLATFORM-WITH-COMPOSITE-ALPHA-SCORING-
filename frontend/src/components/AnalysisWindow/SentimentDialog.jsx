import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

const CONFIGS = {
  POSITIVE: {
    bg: 'from-green-900/60 to-green-800/30',
    border: 'border-green-500/30',
    iconColor: 'text-green-400',
    Icon: TrendingUp,
    particles: ['🎉', '✨', '🚀', '💚', '📈'],
  },
  NEGATIVE: {
    bg: 'from-red-900/60 to-red-800/30',
    border: 'border-red-500/30',
    iconColor: 'text-red-400',
    Icon: TrendingDown,
    particles: [],
  },
  NEUTRAL: {
    bg: 'from-gray-800/60 to-gray-700/30',
    border: 'border-gray-600/30',
    iconColor: 'text-gray-400',
    Icon: Minus,
    particles: [],
  },
}

function Confetti() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {['🎉', '✨', '🚀', '📈'].map((emoji, i) => (
        <motion.span
          key={i}
          className="absolute text-lg"
          initial={{ y: '100%', x: `${20 + i * 20}%`, opacity: 1 }}
          animate={{ y: '-20%', opacity: 0 }}
          transition={{ duration: 2, delay: i * 0.3, repeat: Infinity, repeatDelay: 3 }}
        >
          {emoji}
        </motion.span>
      ))}
    </div>
  )
}

export default function SentimentDialog({ verdict }) {
  if (!verdict) return null
  const { label, message } = verdict
  const config = CONFIGS[label] || CONFIGS.NEUTRAL
  const { bg, border, iconColor, Icon, particles } = config

  return (
    <motion.div
      initial={{ opacity: 0, y: 30, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ type: 'spring', stiffness: 300, damping: 25 }}
      className={`relative overflow-hidden rounded-xl border ${border} bg-gradient-to-r ${bg} p-4`}
    >
      {label === 'POSITIVE' && <Confetti />}
      {label === 'NEGATIVE' && (
        <motion.div
          className="absolute inset-0 rounded-xl border border-red-500/20"
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
        />
      )}

      <div className="relative flex items-center gap-3">
        <motion.div
          animate={label === 'NEGATIVE' ? { scale: [1, 1.1, 1] } : {}}
          transition={{ duration: 1.5, repeat: Infinity }}
          className={`p-2 rounded-full bg-gray-900/50 ${iconColor}`}
        >
          <Icon size={20} />
        </motion.div>
        <div>
          <p className={`text-sm font-bold ${iconColor}`}>
            {label === 'POSITIVE' ? '✅ POSITIVE OUTLOOK' : label === 'NEGATIVE' ? '⚠️ NEGATIVE OUTLOOK' : '➡️ NEUTRAL OUTLOOK'}
          </p>
          <p className="text-gray-300 text-xs mt-0.5">{message}</p>
        </div>
      </div>
    </motion.div>
  )
}
