import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { X, TrendingUp, TrendingDown, Loader2, BarChart2, RefreshCw } from 'lucide-react'
import { getStrategyStocks } from '../../services/stockService'
import useStore from '../../store/useStore'
import { analyzeStock } from '../../services/stockService'

export default function StrategyStocksDrawer({ strategy, onClose }) {
  const [stocks, setStocks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const { setCurrentTicker, setAnalysisResult, setIsAnalyzing, setError: setStoreError } = useStore()

  const fetchStocks = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getStrategyStocks(strategy.id)
      setStocks(data.stocks || [])
    } catch (e) {
      setError('Failed to load stocks. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStocks()
  }, [strategy.id])

  const handleAnalyze = async (ticker) => {
    onClose()
    setCurrentTicker(ticker)
    setIsAnalyzing(true)
    setStoreError(null)
    try {
      const result = await analyzeStock(ticker, 'NSE')
      setAnalysisResult(result)
    } catch (e) {
      setStoreError(e.message)
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <>
      {/* Backdrop */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 z-40"
        onClick={onClose}
      />

      {/* Drawer slides in from left */}
      <motion.div
        initial={{ x: -340 }}
        animate={{ x: 0 }}
        exit={{ x: -340 }}
        transition={{ duration: 0.25, ease: 'easeOut' }}
        className="fixed top-0 left-0 z-50 w-80 h-full bg-gray-900 border-r border-gray-700 flex flex-col shadow-2xl"
      >
        {/* Header */}
        <div className={`px-4 pt-4 pb-3 border-b border-gray-800 ${strategy.bgColor}`}>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <span className="text-2xl">{strategy.emoji}</span>
              <div>
                <h3 className={`text-sm font-bold ${strategy.textColor}`}>{strategy.name}</h3>
                <p className="text-gray-400 text-xs">
                  {loading ? 'Screening...' : `${stocks.length} stocks`}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={fetchStocks}
                className="text-gray-500 hover:text-gray-300 transition-colors p-1.5 rounded-lg hover:bg-gray-800"
                title="Refresh"
              >
                <RefreshCw size={13} />
              </button>
              <button
                onClick={onClose}
                className="text-gray-500 hover:text-gray-300 transition-colors p-1.5 rounded-lg hover:bg-gray-800"
              >
                <X size={14} />
              </button>
            </div>
          </div>

          {/* Criteria chips */}
          <div className="flex flex-wrap gap-1">
            {strategy.criteria.map((c) => (
              <span
                key={c}
                className={`text-xs px-1.5 py-0.5 rounded ${strategy.badgeBg} ${strategy.textColor} leading-tight`}
              >
                {c}
              </span>
            ))}
          </div>
        </div>

        {/* Stock list */}
        <div className="flex-1 overflow-y-auto">
          {loading && (
            <div className="flex flex-col items-center justify-center h-40 gap-3">
              <Loader2 size={22} className="text-india-orange animate-spin" />
              <p className="text-gray-500 text-xs text-center">
                Screening NSE stocks...<br />
                <span className="text-gray-600">This may take ~15 seconds</span>
              </p>
            </div>
          )}

          {error && !loading && (
            <div className="p-6 text-center">
              <p className="text-red-400 text-sm mb-3">{error}</p>
              <button
                onClick={fetchStocks}
                className="text-xs text-india-orange border border-india-orange/30 px-4 py-2 rounded-lg hover:bg-india-orange/10 transition-colors"
              >
                Retry
              </button>
            </div>
          )}

          {!loading && !error && stocks.length === 0 && (
            <div className="flex flex-col items-center justify-center h-40 text-center px-4">
              <p className="text-gray-400 text-sm">No stocks matched at this time.</p>
              <p className="text-gray-600 text-xs mt-1">Market data may be unavailable.</p>
            </div>
          )}

          {!loading && !error && stocks.length > 0 && (
            <div className="p-3 space-y-2">
              {stocks.map((stock, i) => {
                const isUp = (stock.change_pct ?? 0) >= 0
                return (
                  <motion.div
                    key={stock.ticker}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.04 }}
                    className="bg-gray-800 border border-gray-700 rounded-xl p-3 hover:border-gray-600 transition-colors"
                  >
                    {/* Top row */}
                    <div className="flex items-start justify-between mb-2">
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-bold text-white">{stock.ticker}</p>
                        <p className="text-xs text-gray-500 truncate leading-tight">{stock.company_name}</p>
                      </div>
                      <div className="text-right shrink-0 ml-2">
                        <p className="text-sm font-semibold text-white">
                          ₹{stock.price != null ? stock.price.toLocaleString('en-IN') : '—'}
                        </p>
                        <div className={`flex items-center justify-end gap-0.5 text-xs font-medium ${isUp ? 'text-green-400' : 'text-red-400'}`}>
                          {isUp ? <TrendingUp size={10} /> : <TrendingDown size={10} />}
                          {isUp ? '+' : ''}{stock.change_pct?.toFixed(2) ?? '0.00'}%
                        </div>
                      </div>
                    </div>

                    {/* Metrics */}
                    <div className="flex flex-wrap gap-x-3 gap-y-0.5 mb-2.5">
                      {stock.pe_ratio != null && (
                        <span className="text-xs text-gray-500">PE <span className="text-gray-300">{stock.pe_ratio}</span></span>
                      )}
                      {stock.roe != null && (
                        <span className="text-xs text-gray-500">ROE <span className="text-gray-300">{stock.roe}%</span></span>
                      )}
                      {stock.market_cap_cr != null && (
                        <span className="text-xs text-gray-500">
                          MCap <span className="text-gray-300">
                            {stock.market_cap_cr >= 100000
                              ? `₹${(stock.market_cap_cr / 100).toFixed(0)}K Cr`
                              : `₹${stock.market_cap_cr.toLocaleString('en-IN')} Cr`}
                          </span>
                        </span>
                      )}
                      {stock.revenue_growth != null && (
                        <span className="text-xs text-gray-500">Rev <span className={stock.revenue_growth >= 0 ? 'text-green-400' : 'text-red-400'}>{stock.revenue_growth >= 0 ? '+' : ''}{stock.revenue_growth}%</span></span>
                      )}
                    </div>

                    <button
                      onClick={() => handleAnalyze(stock.ticker)}
                      className="w-full flex items-center justify-center gap-1.5 text-xs font-semibold text-india-orange border border-india-orange/30 rounded-lg py-1.5 hover:bg-india-orange/10 transition-colors"
                    >
                      <BarChart2 size={11} />
                      Analyse with AI
                    </button>
                  </motion.div>
                )
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-4 py-2.5 border-t border-gray-800 bg-gray-950">
          <p className="text-gray-700 text-xs text-center">
            Live NSE data · Not SEBI-registered investment advice
          </p>
        </div>
      </motion.div>
    </>
  )
}
