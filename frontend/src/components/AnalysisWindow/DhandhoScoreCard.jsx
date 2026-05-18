import { motion } from 'framer-motion'
import { Zap, TrendingUp, AlertTriangle, Users, Info } from 'lucide-react'

function ScoreBar({ score, color }) {
  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 h-3 bg-gray-800 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${score}%` }}
          transition={{ duration: 1.2, ease: 'easeOut', delay: 0.3 }}
          className="h-full rounded-full"
          style={{ backgroundColor: color }}
        />
      </div>
      <span className="text-sm font-bold text-white w-8 text-right">{score}</span>
    </div>
  )
}

export default function DhandhoScoreCard({ data }) {
  if (!data) return null
  const { dhandho_score, label, color, breakdown = {}, india_context = [],
    one_liner, best_for = [], risk_factors = [], disclaimer } = data

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.4, type: 'spring', stiffness: 200 }}
      className="card border-2"
      style={{ borderColor: color + '40' }}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Zap size={20} style={{ color }} fill={color} />
          <div>
            <h2 className="text-base font-bold text-white leading-none">Alpha Score</h2>
            <p className="text-gray-600 text-xs">Composite AI Rating · NSE/BSE</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.5, type: 'spring', stiffness: 300 }}
            className="text-4xl font-black"
            style={{ color }}
          >
            {dhandho_score}
            <span className="text-lg text-gray-500 font-normal">/100</span>
          </motion.div>
          <span
            className="px-3 py-1 rounded-full text-sm font-bold"
            style={{ backgroundColor: color + '20', color }}
          >
            {label}
          </span>
        </div>
      </div>

      <div className="mb-4">
        <ScoreBar score={dhandho_score} color={color} />
      </div>

      {one_liner && (
        <p className="text-gray-300 text-sm mb-4 italic border-l-2 pl-3" style={{ borderColor: color }}>
          "{one_liner}"
        </p>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        {/* Breakdown */}
        <div className="bg-gray-800 rounded-lg p-3 space-y-2">
          <p className="text-gray-500 text-xs font-semibold uppercase tracking-wide">Score Breakdown</p>
          {[
            ['Fundamental', breakdown.fundamental, '#00C853'],
            ['Technical', breakdown.technical, '#2196F3'],
            ['Sentiment', breakdown.sentiment, '#FFB300'],
          ].map(([name, val, c]) => (
            <div key={name}>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-gray-400">{name}</span>
                <span className="font-semibold" style={{ color: c }}>{val ?? '--'}</span>
              </div>
              <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${val ?? 0}%` }}
                  transition={{ duration: 1, delay: 0.6 }}
                  className="h-full rounded-full"
                  style={{ backgroundColor: c }}
                />
              </div>
            </div>
          ))}
          {breakdown.india_adjustments !== undefined && (
            <div className="text-xs flex justify-between pt-1 border-t border-gray-700">
              <span className="text-gray-500">India Adj.</span>
              <span className={breakdown.india_adjustments >= 0 ? 'text-green-400' : 'text-red-400'}>
                {breakdown.india_adjustments >= 0 ? '+' : ''}{breakdown.india_adjustments}
              </span>
            </div>
          )}
        </div>

        {/* Best For */}
        <div className="bg-gray-800 rounded-lg p-3">
          <p className="text-gray-500 text-xs font-semibold uppercase tracking-wide mb-2 flex items-center gap-1">
            <Users size={10} /> Best For
          </p>
          <div className="space-y-1.5">
            {best_for.map((item, i) => (
              <div key={i} className="flex items-center gap-1.5 text-xs text-gray-300">
                <TrendingUp size={10} className="text-green-400 shrink-0" />
                {item}
              </div>
            ))}
          </div>

          {india_context.length > 0 && (
            <div className="mt-3 space-y-1.5 border-t border-gray-700 pt-2">
              <p className="text-gray-500 text-xs font-semibold uppercase tracking-wide mb-1">India Context</p>
              {india_context.map((ctx, i) => (
                <div key={i} className="text-xs">
                  <span className="text-gray-300">{ctx.factor}</span>
                  <span className={`ml-1.5 font-semibold ${ctx.impact?.startsWith('+') ? 'text-green-400' : 'text-red-400'}`}>
                    ({ctx.impact})
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Risk Factors */}
        <div className="bg-gray-800 rounded-lg p-3">
          <p className="text-gray-500 text-xs font-semibold uppercase tracking-wide mb-2 flex items-center gap-1">
            <AlertTriangle size={10} /> Risk Factors
          </p>
          <div className="space-y-1.5">
            {risk_factors.map((risk, i) => (
              <div key={i} className="flex items-start gap-1.5 text-xs text-gray-300">
                <AlertTriangle size={10} className="text-orange-400 mt-0.5 shrink-0" />
                {risk}
              </div>
            ))}
          </div>
        </div>
      </div>

      {disclaimer && (
        <div className="flex items-start gap-1.5 text-xs text-gray-600 border-t border-gray-800 pt-3">
          <Info size={10} className="mt-0.5 shrink-0" />
          <p>{disclaimer}</p>
        </div>
      )}
    </motion.div>
  )
}
