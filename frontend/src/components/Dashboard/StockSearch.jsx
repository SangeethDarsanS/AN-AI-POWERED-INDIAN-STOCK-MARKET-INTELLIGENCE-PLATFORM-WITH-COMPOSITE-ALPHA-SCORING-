import { useState } from 'react'
import { motion } from 'framer-motion'
import { Search, ChevronDown } from 'lucide-react'
import useStore from '../../store/useStore'
import { analyzeStock } from '../../services/stockService'

const POPULAR = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 'SUNPHARMA', 'SBIN', 'MARUTI']

// Common company name → NSE ticker mapping
const NAME_TO_TICKER = {
  'SUN PHARMA': 'SUNPHARMA',
  'SUN PHARMACEUTICAL': 'SUNPHARMA',
  'HINDUSTAN UNILEVER': 'HINDUNILVR',
  'HUL': 'HINDUNILVR',
  'HDFC BANK': 'HDFCBANK',
  'ICICI BANK': 'ICICIBANK',
  'STATE BANK': 'SBIN',
  'SBI': 'SBIN',
  'TATA MOTORS': 'TATAMOTORS',
  'TATA STEEL': 'TATASTEEL',
  'TATA CONSULTANCY': 'TCS',
  'INFOSYS': 'INFY',
  'BAJAJ FINANCE': 'BAJFINANCE',
  'BAJAJ FINSERV': 'BAJAJFINSV',
  'ASIAN PAINTS': 'ASIANPAINT',
  'DR REDDY': 'DRREDDY',
  'DR. REDDY': 'DRREDDY',
  'NESTLE': 'NESTLEIND',
  'ULTRA CEMCO': 'ULTRACEMCO',
  'ULTRATECH': 'ULTRACEMCO',
}

export default function StockSearch() {
  const [ticker, setTicker] = useState('')
  const [exchange, setExchange] = useState('NSE')
  const { setAnalysisResult, setIsAnalyzing, setCurrentTicker, setCurrentExchange, setError, addToWatchlist } = useStore()

  const handleAnalyze = async (sym = ticker, exch = exchange) => {
    if (!sym.trim()) return
    const raw = sym.trim().toUpperCase()
    // Resolve common company names to NSE ticker symbols
    const t = NAME_TO_TICKER[raw] || raw
    setCurrentTicker(t)
    setCurrentExchange(exch)
    setIsAnalyzing(true)
    setError(null)
    try {
      const result = await analyzeStock(t, exch)
      setAnalysisResult(result)
      addToWatchlist(t)
    } catch (e) {
      setError(e.message)
      setAnalysisResult(null)
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
            onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
            placeholder="Enter ticker: RELIANCE, TCS, INFY..."
            className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-9 pr-4 py-2.5 text-white placeholder-gray-500 text-sm focus:outline-none focus:border-india-orange transition-colors"
          />
        </div>
        <div className="relative">
          <select
            value={exchange}
            onChange={(e) => setExchange(e.target.value)}
            className="appearance-none bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5 pr-7 text-white text-sm focus:outline-none focus:border-india-orange cursor-pointer"
          >
            <option value="NSE">NSE</option>
            <option value="BSE">BSE</option>
          </select>
          <ChevronDown size={12} className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 pointer-events-none" />
        </div>
        <motion.button
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.97 }}
          onClick={() => handleAnalyze()}
          className="btn-primary"
        >
          Analyze
        </motion.button>
      </div>

      <div className="flex flex-wrap gap-1.5">
        {POPULAR.map((sym) => (
          <motion.button
            key={sym}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => { setTicker(sym); handleAnalyze(sym, exchange) }}
            className="px-2.5 py-1 rounded-md bg-gray-800 border border-gray-700 text-gray-300 text-xs font-medium hover:border-india-orange hover:text-india-orange transition-colors"
          >
            {sym}
          </motion.button>
        ))}
      </div>
    </div>
  )
}
