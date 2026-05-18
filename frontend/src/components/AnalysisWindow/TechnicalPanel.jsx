import { motion } from 'framer-motion'
import { CheckCircle, XCircle } from 'lucide-react'

function RSIGauge({ value }) {
  if (value == null) return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-gray-500">RSI (14)</span>
        <span className="text-gray-700">N/A</span>
      </div>
      <div className="h-2 bg-gray-800 rounded-full" />
    </div>
  )
  const color = value < 30 ? '#00C853' : value > 70 ? '#D50000' : '#FFB300'
  const label = value < 30 ? 'Oversold' : value > 70 ? 'Overbought' : 'Neutral'
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-gray-400">RSI ({value.toFixed(1)})</span>
        <span style={{ color }} className="font-semibold">{label}</span>
      </div>
      <div className="h-2 bg-gray-800 rounded-full overflow-hidden relative">
        {/* Zone markers */}
        <div className="absolute left-[30%] top-0 h-full w-px bg-gray-600 opacity-50" />
        <div className="absolute left-[70%] top-0 h-full w-px bg-gray-600 opacity-50" />
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${Math.min(100, Math.max(0, value))}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className="h-full rounded-full"
          style={{ backgroundColor: color }}
        />
      </div>
      <div className="flex justify-between text-gray-700 text-xs">
        <span>0 Oversold</span>
        <span>30</span>
        <span>70</span>
        <span>Overbought 100</span>
      </div>
    </div>
  )
}

function MAIndicator({ label, active }) {
  return (
    <div className="flex items-center justify-between py-1">
      <span className="text-gray-400 text-xs">{label}</span>
      {active
        ? <CheckCircle size={14} className="text-green-400" />
        : <XCircle size={14} className="text-red-400" />
      }
    </div>
  )
}

function EMARow({ label, ema, current }) {
  if (ema == null) return null
  const above = current != null && current > ema
  return (
    <div className="flex justify-between items-center py-0.5">
      <span className="text-gray-500 text-xs">{label}</span>
      <div className="flex items-center gap-2">
        <span className="text-gray-300 text-xs font-mono">₹{ema.toLocaleString('en-IN')}</span>
        <span className={`text-xs font-semibold ${above ? 'text-green-400' : 'text-red-400'}`}>
          {above ? '▲' : '▼'}
        </span>
      </div>
    </div>
  )
}

function ScoreBadge({ score }) {
  const color = score >= 70 ? 'text-green-400 bg-green-400/10 border-green-400/30'
    : score >= 40 ? 'text-yellow-400 bg-yellow-400/10 border-yellow-400/30'
    : 'text-red-400 bg-red-400/10 border-red-400/30'
  return (
    <div className={`inline-flex items-center justify-center w-12 h-12 rounded-full border-2 ${color} text-lg font-bold`}>
      {score}
    </div>
  )
}

function SectionHeader({ label }) {
  return <p className="text-gray-600 text-xs font-semibold uppercase tracking-wider pt-2 pb-0.5">{label}</p>
}

export default function TechnicalPanel({ data }) {
  if (!data) return null
  const {
    technical_score, trend, current_price,
    rsi,
    macd_signal, macd_line, macd_hist,
    moving_averages = {},
    bollinger_bands = {},
    adx,
    support, resistance,
    volume_signal, supertrend,
    summary, chart_patterns = [],
  } = data

  const trendColor = trend === 'BULLISH' ? 'text-green-400 bg-green-400/10'
    : trend === 'BEARISH' ? 'text-red-400 bg-red-400/10'
    : 'text-gray-400 bg-gray-400/10'

  const supertrendColor = supertrend === 'BUY' ? 'text-green-400 bg-green-400/10'
    : supertrend === 'SELL' ? 'text-red-400 bg-red-400/10'
    : 'text-gray-400 bg-gray-400/10'

  const macdColor = macd_signal?.includes('BULLISH') ? 'text-green-400'
    : macd_signal?.includes('BEARISH') ? 'text-red-400'
    : 'text-gray-400'

  const adxLabel = adx == null ? null : adx > 50 ? 'Very Strong' : adx > 25 ? 'Strong' : adx > 15 ? 'Moderate' : 'Weak'
  const adxColor = adx == null ? 'text-gray-700' : adx > 25 ? 'text-green-400' : adx > 15 ? 'text-yellow-400' : 'text-gray-500'

  const bbPos = bollinger_bands.position
  const bbColor = bbPos === 'UPPER' ? 'text-red-400' : bbPos === 'LOWER' ? 'text-green-400' : 'text-yellow-400'

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="card h-full"
    >
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-bold text-gray-200 uppercase tracking-wide">Technical</h3>
        <ScoreBadge score={technical_score} />
      </div>

      <div className="flex gap-2 mb-3">
        <span className={`badge text-xs font-bold ${trendColor}`}>{trend}</span>
        <span className={`badge text-xs font-bold ${supertrendColor}`}>ST: {supertrend}</span>
        {adxLabel && (
          <span className={`badge text-xs font-semibold bg-gray-800 ${adxColor}`}>
            ADX: {adx?.toFixed(1)} ({adxLabel})
          </span>
        )}
      </div>

      {/* RSI */}
      <div className="mb-3">
        <RSIGauge value={rsi} />
      </div>

      {/* MACD */}
      <SectionHeader label="MACD" />
      <div className="bg-gray-800/60 rounded-lg px-2 py-1.5 mb-3 space-y-0.5">
        <div className="flex justify-between text-xs">
          <span className="text-gray-500">Signal</span>
          <span className={`font-semibold ${macdColor}`}>{macd_signal?.replace(/_/g, ' ')}</span>
        </div>
        {macd_line != null && (
          <div className="flex justify-between text-xs">
            <span className="text-gray-500">MACD Line</span>
            <span className={`font-mono ${macd_line >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {macd_line.toFixed(2)}
            </span>
          </div>
        )}
        {macd_hist != null && (
          <div className="flex justify-between text-xs">
            <span className="text-gray-500">Histogram</span>
            <span className={`font-mono ${macd_hist >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {macd_hist.toFixed(2)}
            </span>
          </div>
        )}
      </div>

      {/* Moving Averages — checkboxes */}
      <div className="border border-gray-800 rounded-lg p-2 mb-3">
        <p className="text-xs text-gray-500 mb-1 font-medium">Moving Averages</p>
        <MAIndicator label="Above 50 DMA" active={moving_averages.above_50dma} />
        <MAIndicator label="Above 200 DMA" active={moving_averages.above_200dma} />
        <MAIndicator label="Golden Cross (50 > 200)" active={moving_averages.golden_cross} />
        {moving_averages.death_cross && (
          <div className="flex items-center justify-between py-1">
            <span className="text-red-400 text-xs">⚠ Death Cross Active</span>
          </div>
        )}
      </div>

      {/* EMA Values */}
      {(moving_averages.ema20 || moving_averages.ema50 || moving_averages.ema200) && (
        <div className="bg-gray-800/60 rounded-lg px-2 py-1.5 mb-3">
          <p className="text-gray-600 text-xs font-semibold uppercase tracking-wider mb-1">EMA Levels</p>
          <EMARow label="EMA 20" ema={moving_averages.ema20} current={current_price} />
          <EMARow label="EMA 50" ema={moving_averages.ema50} current={current_price} />
          <EMARow label="EMA 200" ema={moving_averages.ema200} current={current_price} />
        </div>
      )}

      {/* Support / Resistance */}
      <div className="grid grid-cols-2 gap-2 mb-3">
        <div className="bg-gray-800 rounded-lg p-2 text-center">
          <p className="text-gray-500 text-xs">Support</p>
          <p className="text-green-400 text-sm font-bold">
            {support != null ? `₹${support.toLocaleString('en-IN')}` : '--'}
          </p>
        </div>
        <div className="bg-gray-800 rounded-lg p-2 text-center">
          <p className="text-gray-500 text-xs">Resistance</p>
          <p className="text-red-400 text-sm font-bold">
            {resistance != null ? `₹${resistance.toLocaleString('en-IN')}` : '--'}
          </p>
        </div>
      </div>

      {/* Bollinger Bands */}
      {bollinger_bands.upper != null && (
        <div className="bg-gray-800/60 rounded-lg px-2 py-1.5 mb-3">
          <div className="flex justify-between text-xs mb-1">
            <span className="text-gray-600 font-semibold uppercase tracking-wider">Bollinger Bands</span>
            <span className={`font-semibold ${bbColor}`}>{bbPos}</span>
          </div>
          <div className="flex justify-between text-xs text-gray-400">
            <span>Lower: ₹{bollinger_bands.lower?.toLocaleString('en-IN')}</span>
            <span>Mid: ₹{bollinger_bands.middle?.toLocaleString('en-IN')}</span>
            <span>Upper: ₹{bollinger_bands.upper?.toLocaleString('en-IN')}</span>
          </div>
        </div>
      )}

      {/* Volume */}
      <div className="flex items-center gap-2 mb-2">
        <span className="text-gray-500 text-xs">Volume:</span>
        <span className={`text-xs font-semibold ${
          volume_signal === 'ABOVE_AVERAGE' ? 'text-green-400' :
          volume_signal === 'BELOW_AVERAGE' ? 'text-red-400' : 'text-gray-400'
        }`}>
          {volume_signal?.replace(/_/g, ' ')}
        </span>
      </div>

      {chart_patterns.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-2">
          {chart_patterns.map((p, i) => (
            <span key={i} className="badge text-xs bg-purple-400/10 text-purple-400 border border-purple-400/20">{p}</span>
          ))}
        </div>
      )}

      {summary && (
        <p className="text-gray-400 text-xs leading-relaxed border-t border-gray-800 pt-3">
          {summary}
        </p>
      )}
    </motion.div>
  )
}
