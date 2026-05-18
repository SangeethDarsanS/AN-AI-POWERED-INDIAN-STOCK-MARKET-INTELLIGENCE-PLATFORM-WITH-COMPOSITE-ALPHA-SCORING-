import { motion } from 'framer-motion'
import { AlertTriangle, CheckCircle } from 'lucide-react'

function formatMarketCap(mc) {
  if (!mc) return null
  const cr = mc / 10_000_000  // 1 Crore = 10,000,000
  if (cr >= 100_000) return `₹${(cr / 100_000).toFixed(2)}L Cr`
  if (cr >= 1_000) return `₹${(cr / 1_000).toFixed(2)}K Cr`
  return `₹${cr.toFixed(0)} Cr`
}

function MetricRow({ label, value, suffix = '', good, warn, isText }) {
  const isNull = value === null || value === undefined
  const formatted = isNull
    ? 'N/A'
    : isText
      ? String(value)
      : (typeof value === 'number' ? value.toFixed(2) : String(value)) + suffix

  let textColor = 'text-gray-600'
  if (!isNull && !isText) {
    if (good === true) textColor = 'text-green-400'
    else if (good === false) textColor = 'text-red-400'
    else if (warn === true) textColor = 'text-yellow-400'
    else textColor = 'text-gray-300'
  } else if (!isNull && isText) {
    if (good === true) textColor = 'text-green-400'
    else if (good === false) textColor = 'text-red-400'
    else textColor = 'text-gray-400'
  }

  return (
    <div className="flex justify-between items-center py-1.5 border-b border-gray-800 last:border-0">
      <span className="text-gray-500 text-xs">{label}</span>
      <span className={`text-xs font-semibold ${isNull ? 'text-gray-700' : textColor}`}>
        {formatted}
      </span>
    </div>
  )
}

function SectionHeader({ label }) {
  return (
    <p className="text-gray-600 text-xs font-semibold uppercase tracking-wider pt-2 pb-0.5">
      {label}
    </p>
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

export default function FundamentalPanel({ data }) {
  if (!data) return null
  const {
    fundamental_score, verdict,
    pe_ratio, pb_ratio, eps, market_cap, current_price, week52_high, week52_low,
    roe, roce, debt_equity,
    promoter_holding, fii_trend,
    revenue_growth_yoy, net_profit_growth,
    gross_margins, net_profit_margin,
    dividend_yield,
    summary, flags,
  } = data

  const fmtMc = formatMarketCap(market_cap)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
      className="card h-full"
    >
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-bold text-gray-200 uppercase tracking-wide">Fundamental</h3>
        <ScoreBadge score={fundamental_score} />
      </div>

      <div className="inline-flex items-center gap-1 mb-3">
        <span className={`badge text-xs font-bold ${
          verdict === 'STRONG' ? 'bg-green-400/10 text-green-400' :
          verdict === 'WEAK'   ? 'bg-red-400/10 text-red-400' :
                                 'bg-yellow-400/10 text-yellow-400'
        }`}>
          {verdict === 'STRONG' ? <CheckCircle size={10} className="mr-1 inline" /> :
           verdict === 'WEAK'   ? <AlertTriangle size={10} className="mr-1 inline" /> : null}
          {verdict}
        </span>
      </div>

      {/* Price & Market Cap */}
      <SectionHeader label="Valuation" />
      <div className="space-y-0">
        {current_price != null && (
          <MetricRow label="Price" value={`₹${current_price?.toLocaleString('en-IN')}`} isText good />
        )}
        {fmtMc && (
          <MetricRow label="Market Cap" value={fmtMc} isText />
        )}
        <MetricRow label="P/E Ratio"  value={pe_ratio}  good={pe_ratio != null && pe_ratio < 30} />
        <MetricRow label="P/B Ratio"  value={pb_ratio}  good={pb_ratio != null && pb_ratio < 3} />
        <MetricRow label="EPS (TTM)"  value={eps} suffix=" ₹" good={eps != null && eps > 0} />
      </div>

      {/* 52-week range */}
      {(week52_high != null || week52_low != null) && (
        <div className="my-2 bg-gray-800/60 rounded-lg px-2 py-1.5">
          <p className="text-gray-600 text-xs mb-1">52-Week Range</p>
          <div className="flex items-center justify-between text-xs">
            <span className="text-red-400 font-semibold">₹{week52_low?.toLocaleString('en-IN') ?? '--'}</span>
            <div className="flex-1 mx-2 h-1 bg-gray-700 rounded-full overflow-hidden">
              {week52_high != null && week52_low != null && current_price != null && (
                <div
                  className="h-full bg-india-orange rounded-full"
                  style={{ width: `${Math.min(100, Math.max(0, ((current_price - week52_low) / (week52_high - week52_low)) * 100))}%` }}
                />
              )}
            </div>
            <span className="text-green-400 font-semibold">₹{week52_high?.toLocaleString('en-IN') ?? '--'}</span>
          </div>
        </div>
      )}

      {/* Returns */}
      <SectionHeader label="Returns & Leverage" />
      <div className="space-y-0">
        <MetricRow label="ROE"          value={roe}          suffix="%" good={roe != null && roe > 15} />
        <MetricRow label="ROCE"         value={roce}         suffix="%" good={roce != null && roce > 12} />
        <MetricRow label="Debt/Equity"  value={debt_equity}  good={debt_equity != null && debt_equity < 0.5}
                                                             warn={debt_equity != null && debt_equity >= 0.5 && debt_equity < 1.5} />
      </div>

      {/* Margins */}
      <SectionHeader label="Margins & Growth" />
      <div className="space-y-0">
        <MetricRow label="Gross Margin"   value={gross_margins}     suffix="%" good={gross_margins != null && gross_margins > 30} />
        <MetricRow label="Net Margin"     value={net_profit_margin} suffix="%" good={net_profit_margin != null && net_profit_margin > 10} />
        <MetricRow label="Revenue Growth" value={revenue_growth_yoy} suffix="%" good={revenue_growth_yoy != null && revenue_growth_yoy > 0} />
        <MetricRow label="Profit Growth"  value={net_profit_growth}  suffix="%" good={net_profit_growth != null && net_profit_growth > 0} />
        <MetricRow label="Dividend Yield" value={dividend_yield}     suffix="%" good={dividend_yield != null && dividend_yield > 0} />
      </div>

      {/* Holdings */}
      <SectionHeader label="Holdings" />
      <div className="space-y-0">
        {promoter_holding != null
          ? <MetricRow label="Promoter %" value={promoter_holding} suffix="%" good={promoter_holding > 50} />
          : <MetricRow label="Promoter %" value={null} />
        }
        <MetricRow label="FII Trend" value={fii_trend === 'UNKNOWN' ? null : fii_trend} isText />
      </div>

      {summary && (
        <p className="text-gray-400 text-xs mt-3 leading-relaxed border-t border-gray-800 pt-3">
          {summary}
        </p>
      )}

      {flags && flags.length > 0 && (
        <div className="mt-3 space-y-1">
          {flags.map((flag, i) => (
            <div key={i} className="flex items-center gap-1.5 text-xs text-red-400">
              <AlertTriangle size={10} />
              {flag}
            </div>
          ))}
        </div>
      )}
    </motion.div>
  )
}
