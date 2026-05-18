import { motion, AnimatePresence } from 'framer-motion'
import { BarChart2, Search } from 'lucide-react'
import useStore from '../../store/useStore'
import StockSearch from '../Dashboard/StockSearch'
import WatchlistPanel from '../Dashboard/WatchlistPanel'
import FundamentalPanel from './FundamentalPanel'
import TechnicalPanel from './TechnicalPanel'
import NewsPanel from './NewsPanel'
import SentimentDialog from './SentimentDialog'
import DhandhoScoreCard from './DhandhoScoreCard'
import SMDPanel from './SMDPanel'
import Loader from '../shared/Loader'

function EmptyState() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex flex-col items-center justify-center py-16 text-center"
    >
      <motion.div
        animate={{ y: [0, -8, 0] }}
        transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
        className="text-6xl mb-4"
      >
        🇮🇳
      </motion.div>
      <h2 className="text-2xl font-bold text-white mb-2">StockAI</h2>
      <p className="text-gray-400 text-sm mb-6 max-w-sm">
        Search any NSE/BSE stock above to get AI-powered Fundamental + Technical + Sentiment analysis with the Alpha Score
      </p>
      <div className="grid grid-cols-3 gap-3 max-w-xs">
        {[
          { icon: '📊', label: 'Fundamental' },
          { icon: '📈', label: 'Technical' },
          { icon: '📰', label: 'Sentiment' },
        ].map((item) => (
          <div key={item.label} className="bg-gray-900 border border-gray-800 rounded-xl p-3 text-center">
            <div className="text-2xl mb-1">{item.icon}</div>
            <p className="text-gray-400 text-xs">{item.label}</p>
          </div>
        ))}
      </div>
      <div className="mt-4 bg-gray-900 border border-india-orange/30 rounded-xl px-4 py-3">
        <p className="text-india-orange text-xs font-semibold">⚡ Alpha Score</p>
        <p className="text-gray-400 text-xs mt-1">Composite AI rating 0–100 — Fundamental + Technical + Sentiment</p>
      </div>
    </motion.div>
  )
}

export default function AnalysisWindow() {
  const { analysisResult, isAnalyzing, error, currentTicker } = useStore()

  return (
    <div className="flex flex-col h-full gap-4 overflow-y-auto pr-1">
      <div className="card">
        <div className="flex items-center gap-2 mb-3">
          <BarChart2 size={16} className="text-india-orange" />
          <h2 className="text-sm font-bold text-gray-200">Stock Analysis</h2>
          {currentTicker && (
            <span className="ml-auto text-xs font-bold text-india-orange bg-india-orange/10 px-2 py-0.5 rounded-full">
              {currentTicker}
            </span>
          )}
        </div>
        <StockSearch />
      </div>

      <WatchlistPanel />

      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="bg-red-900/20 border border-red-500/30 rounded-xl p-3 text-red-400 text-sm"
        >
          ⚠️ {error}
        </motion.div>
      )}

      <AnimatePresence mode="wait">
        {isAnalyzing && (
          <motion.div key="loader" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <Loader text="Running AI analysis for Indian market data..." size="lg" />
          </motion.div>
        )}

        {!isAnalyzing && !analysisResult && !error && (
          <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <EmptyState />
          </motion.div>
        )}

        {!isAnalyzing && analysisResult && (
          <motion.div
            key="result"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="space-y-4"
          >
            {/* Sentiment Dialog */}
            {analysisResult.sentiment?.dialog_verdict && (
              <SentimentDialog verdict={analysisResult.sentiment.dialog_verdict} />
            )}

            {/* Three panel grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              <FundamentalPanel data={analysisResult.fundamental} />
              <TechnicalPanel data={analysisResult.technical} />
              <NewsPanel data={analysisResult.sentiment} />
            </div>

            {/* Sentiment Momentum Divergence */}
            <SMDPanel ticker={analysisResult.ticker} />

            {/* Alpha Score */}
            {analysisResult.dhandho && (
              <DhandhoScoreCard data={analysisResult.dhandho} />
            )}

            <p className="text-gray-700 text-xs text-center pb-2">
              ⚠️ This analysis is AI-generated for informational purposes only. Not SEBI-registered investment advice. Please consult a certified financial advisor before investing.
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
