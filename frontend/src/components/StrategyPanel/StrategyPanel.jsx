import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronLeft, ChevronRight, Target } from 'lucide-react'
import { STRATEGIES } from '../../constants/strategies'
import StrategyStocksDrawer from './StrategyStocksDrawer'

export default function StrategyPanel() {
  const [collapsed, setCollapsed] = useState(false)
  const [selectedStrategy, setSelectedStrategy] = useState(null)
  const [drawerOpen, setDrawerOpen] = useState(false)

  const handleStrategyClick = (strategy) => {
    setSelectedStrategy(strategy)
    setDrawerOpen(true)
  }

  return (
    <>
      <motion.aside
        animate={{ width: collapsed ? 44 : 220 }}
        transition={{ duration: 0.25, ease: 'easeInOut' }}
        className="shrink-0 relative flex flex-col bg-gray-900 border-r border-gray-800 overflow-hidden"
        style={{ minHeight: 'calc(100vh - 140px)' }}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-3 py-3 border-b border-gray-800">
          {!collapsed && (
            <div className="flex items-center gap-2 overflow-hidden">
              <Target size={14} className="text-india-orange shrink-0" />
              <span className="text-xs font-bold text-gray-200 whitespace-nowrap">Strategy Stocks</span>
            </div>
          )}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="ml-auto text-gray-500 hover:text-gray-300 transition-colors p-0.5 rounded"
          >
            {collapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
          </button>
        </div>

        {/* Strategy List */}
        <div className="flex-1 overflow-y-auto py-2 px-2 space-y-1.5">
          {STRATEGIES.map((strategy) => (
            <motion.button
              key={strategy.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => handleStrategyClick(strategy)}
              className={`w-full text-left rounded-lg border transition-all ${
                selectedStrategy?.id === strategy.id && drawerOpen
                  ? `${strategy.borderColor} ${strategy.bgColor}`
                  : 'border-gray-800 bg-gray-800/50 hover:border-gray-700'
              } ${collapsed ? 'p-2 flex items-center justify-center' : 'p-2.5'}`}
              title={collapsed ? strategy.name : undefined}
            >
              {collapsed ? (
                <span className="text-lg">{strategy.emoji}</span>
              ) : (
                <>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-base">{strategy.emoji}</span>
                    <span className={`text-xs font-semibold ${strategy.textColor} leading-tight`}>
                      {strategy.name}
                    </span>
                  </div>
                  <p className="text-gray-500 text-xs leading-tight line-clamp-2">
                    {strategy.description}
                  </p>
                </>
              )}
            </motion.button>
          ))}
        </div>

        {/* Bottom hint */}
        {!collapsed && (
          <div className="px-3 py-2 border-t border-gray-800">
            <p className="text-gray-700 text-xs text-center">Click strategy to screen stocks</p>
          </div>
        )}
      </motion.aside>

      <AnimatePresence>
        {drawerOpen && selectedStrategy && (
          <StrategyStocksDrawer
            strategy={selectedStrategy}
            onClose={() => setDrawerOpen(false)}
          />
        )}
      </AnimatePresence>
    </>
  )
}
