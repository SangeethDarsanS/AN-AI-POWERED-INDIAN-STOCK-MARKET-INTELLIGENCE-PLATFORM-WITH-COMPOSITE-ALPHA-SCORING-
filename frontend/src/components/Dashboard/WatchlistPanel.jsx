import { motion } from 'framer-motion'
import { X, Star, TrendingUp } from 'lucide-react'
import useStore from '../../store/useStore'
import { analyzeStock } from '../../services/stockService'

export default function WatchlistPanel() {
  const { watchlist, removeFromWatchlist, setAnalysisResult, setIsAnalyzing, setCurrentTicker, setError } = useStore()

  const handleClick = async (ticker) => {
    setCurrentTicker(ticker)
    setIsAnalyzing(true)
    try {
      const result = await analyzeStock(ticker, 'NSE')
      setAnalysisResult(result)
    } catch (e) {
      setError(e.message)
    } finally {
      setIsAnalyzing(false)
    }
  }

  if (watchlist.length === 0) return null

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-3">
        <Star size={14} className="text-yellow-400" />
        <span className="text-sm font-semibold text-gray-300">Watchlist</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {watchlist.map((ticker) => (
          <motion.div
            key={ticker}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex items-center gap-1.5 bg-gray-800 border border-gray-700 rounded-lg px-2.5 py-1"
          >
            <button
              onClick={() => handleClick(ticker)}
              className="text-xs font-medium text-gray-200 hover:text-india-orange transition-colors flex items-center gap-1"
            >
              <TrendingUp size={10} />
              {ticker}
            </button>
            <button
              onClick={() => removeFromWatchlist(ticker)}
              className="text-gray-600 hover:text-red-400 transition-colors"
            >
              <X size={10} />
            </button>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
