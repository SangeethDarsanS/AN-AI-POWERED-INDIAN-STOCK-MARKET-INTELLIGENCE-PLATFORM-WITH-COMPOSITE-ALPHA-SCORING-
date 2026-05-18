import { motion } from 'framer-motion'

const ACTIONS = [
  { emoji: '📈', label: 'Top Gainers', message: 'Show me top gainers on NSE today' },
  { emoji: '📉', label: 'Top Losers', message: 'Show me top losers on NSE today' },
  { emoji: '🏦', label: 'NIFTY Level', message: 'What is NIFTY 50 trading at right now?' },
  { emoji: '📰', label: 'Market News', message: 'What are the latest market news?' },
  { emoji: '📅', label: 'Results', message: 'Which companies declare results this week?' },
  { emoji: '💡', label: 'Market Mood', message: 'Is the market bullish or bearish today?' },
]

export default function QuickActions({ onAction }) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-1 px-1">
      {ACTIONS.map((action, i) => (
        <motion.button
          key={action.label}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.05 }}
          whileHover={{ scale: 1.05, y: -1 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => onAction(action.message)}
          className="shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-gray-800 border border-gray-700 hover:border-india-orange hover:bg-india-orange/10 text-gray-300 hover:text-india-orange transition-all duration-200 text-xs font-medium"
        >
          <span>{action.emoji}</span>
          <span>{action.label}</span>
        </motion.button>
      ))}
    </div>
  )
}
