import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ReferenceLine, ResponsiveContainer,
} from 'recharts'
import { TrendingUp, TrendingDown, Minus, Activity, AlertCircle } from 'lucide-react'
import { getSMD } from '../../services/stockService'

// ── Signal config ────────────────────────────────────────────────────────────
const SIGNAL_CONFIG = {
  BULLISH_CROSSOVER: {
    label: 'Bullish Crossover',
    color: '#00E676',
    bg: 'bg-green-500/20',
    border: 'border-green-500/40',
    text: 'text-green-400',
    Icon: TrendingUp,
  },
  BULLISH: {
    label: 'Bullish',
    color: '#69F0AE',
    bg: 'bg-green-500/10',
    border: 'border-green-500/30',
    text: 'text-green-500',
    Icon: TrendingUp,
  },
  BEARISH_CROSSOVER: {
    label: 'Bearish Crossover',
    color: '#FF1744',
    bg: 'bg-red-500/20',
    border: 'border-red-500/40',
    text: 'text-red-400',
    Icon: TrendingDown,
  },
  BEARISH: {
    label: 'Bearish',
    color: '#FF6D6D',
    bg: 'bg-red-500/10',
    border: 'border-red-500/30',
    text: 'text-red-400',
    Icon: TrendingDown,
  },
  NEUTRAL: {
    label: 'Neutral',
    color: '#9E9E9E',
    bg: 'bg-gray-500/10',
    border: 'border-gray-500/30',
    text: 'text-gray-400',
    Icon: Minus,
  },
}

const CONFIDENCE_COLOR = {
  HIGH: 'text-green-400',
  MEDIUM: 'text-yellow-400',
  LOW: 'text-gray-500',
}

// ── Custom tooltip ───────────────────────────────────────────────────────────
function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-gray-900 border border-gray-700 rounded-lg p-2 text-xs space-y-1 shadow-xl">
      <p className="text-gray-400 font-mono">{label}</p>
      {payload.map((p) => (
        <p key={p.name} style={{ color: p.color }}>
          {p.name}: <span className="font-bold">{p.value?.toFixed(1)}</span>
        </p>
      ))}
    </div>
  )
}

// ── Main component ───────────────────────────────────────────────────────────
export default function SMDPanel({ ticker }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!ticker) return
    setLoading(true)
    setError(null)
    getSMD(ticker)
      .then(setData)
      .catch(() => setError('Could not load SMD data.'))
      .finally(() => setLoading(false))
  }, [ticker])

  if (loading) {
    return (
      <div className="card flex items-center gap-2 text-gray-500 text-sm py-4">
        <Activity size={14} className="animate-pulse text-purple-400" />
        Computing Sentiment Momentum Divergence…
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="card flex items-center gap-2 text-gray-600 text-sm py-3">
        <AlertCircle size={14} />
        {error ?? 'No SMD data available.'}
      </div>
    )
  }

  const signal = SIGNAL_CONFIG[data.signal] ?? SIGNAL_CONFIG.NEUTRAL
  const SignalIcon = signal.Icon
  const hasChart = data.history?.length >= 2

  // Format chart data — abbreviate date for X axis
  const chartData = data.history.map((pt) => ({
    date: pt.date.slice(5),      // "MM-DD"
    Score: pt.sentiment_score,
    EMA3: pt.ema3,
    EMA14: pt.ema14,
    SMD: pt.smd,
  }))

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="card space-y-4"
    >
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-2">
          <Activity size={15} className="text-purple-400" />
          <h3 className="text-sm font-bold text-gray-200">
            Sentiment Momentum Divergence
            <span className="ml-1 text-gray-600 font-normal text-xs">(SMD)</span>
          </h3>
        </div>
        {/* Signal badge */}
        <span className={`flex items-center gap-1 text-xs font-bold px-2.5 py-1 rounded-full border ${signal.bg} ${signal.border} ${signal.text}`}>
          <SignalIcon size={11} />
          {signal.label}
        </span>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-4 gap-2 text-center">
        {[
          { label: 'SMD', value: data.smd_value > 0 ? `+${data.smd_value}` : `${data.smd_value}`, color: data.smd_value > 2 ? 'text-green-400' : data.smd_value < -2 ? 'text-red-400' : 'text-gray-300' },
          { label: 'EMA-3', value: data.ema3.toFixed(1), color: 'text-sky-400' },
          { label: 'EMA-14', value: data.ema14.toFixed(1), color: 'text-orange-400' },
          { label: 'Days', value: data.data_points, color: 'text-gray-300' },
        ].map(({ label, value, color }) => (
          <div key={label} className="bg-gray-900 rounded-lg p-2">
            <p className="text-gray-500 text-xs mb-0.5">{label}</p>
            <p className={`text-sm font-bold font-mono ${color}`}>{value}</p>
          </div>
        ))}
      </div>

      {/* Chart */}
      {hasChart ? (
        <div className="h-44">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f1f1f" />
              <XAxis dataKey="date" tick={{ fill: '#555', fontSize: 9 }} />
              <YAxis tick={{ fill: '#555', fontSize: 9 }} domain={['auto', 'auto']} />
              <Tooltip content={<CustomTooltip />} />
              <ReferenceLine y={0} stroke="#444" strokeDasharray="4 4" />
              <Legend wrapperStyle={{ fontSize: '10px', color: '#888' }} />
              <Line type="monotone" dataKey="Score" stroke="#4FC3F7" dot={false} strokeWidth={1} opacity={0.5} />
              <Line type="monotone" dataKey="EMA3" stroke="#69F0AE" dot={false} strokeWidth={1.5} />
              <Line type="monotone" dataKey="EMA14" stroke="#FFB74D" dot={false} strokeWidth={1.5} />
              <Line type="monotone" dataKey="SMD" stroke="#CE93D8" dot={false} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="bg-gray-900 rounded-lg p-3 text-center text-xs text-gray-500">
          📈 Chart builds as you analyse this stock daily.<br />
          <span className="text-gray-600">Need at least 2 days of data.</span>
        </div>
      )}

      {/* Interpretation */}
      <div className={`rounded-lg border px-3 py-2 text-xs leading-relaxed ${signal.bg} ${signal.border} ${signal.text}`}>
        {data.interpretation}
      </div>

      {/* Confidence footer */}
      <div className="flex items-center justify-between text-xs text-gray-600">
        <span>
          Confidence:{' '}
          <span className={`font-bold ${CONFIDENCE_COLOR[data.confidence]}`}>
            {data.confidence}
          </span>
          {data.confidence !== 'HIGH' && ' — run daily analyses to improve accuracy'}
        </span>
        <span className="text-gray-700">SMD = EMA(3) − EMA(14)</span>
      </div>
    </motion.div>
  )
}
