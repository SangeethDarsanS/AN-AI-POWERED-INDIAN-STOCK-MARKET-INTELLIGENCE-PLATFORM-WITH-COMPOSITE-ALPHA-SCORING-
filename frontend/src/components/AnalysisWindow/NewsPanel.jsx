import { motion } from 'framer-motion'
import { Newspaper, ExternalLink, Clock } from 'lucide-react'

function SentimentBadge({ sentiment }) {
  const styles = {
    POSITIVE: 'bg-green-400/10 text-green-400',
    NEGATIVE: 'bg-red-400/10 text-red-400',
    NEUTRAL: 'bg-gray-400/10 text-gray-400',
  }
  return <span className={`badge text-xs ${styles[sentiment] || styles.NEUTRAL}`}>{sentiment}</span>
}

function ImpactBadge({ impact }) {
  const styles = {
    HIGH:   'bg-orange-400/10 text-orange-400',
    MEDIUM: 'bg-blue-400/10 text-blue-400',
    LOW:    'bg-gray-400/10 text-gray-500',
  }
  return <span className={`badge text-xs ${styles[impact] || styles.LOW}`}>{impact}</span>
}

function ConfidencePip({ pct }) {
  // Extract confidence % from reason string, e.g. "FinBERT financial sentiment — positive (87% confidence)"
  if (!pct) return null
  return (
    <span className="text-gray-600 text-xs">
      {pct}
    </span>
  )
}

function formatTimestamp(ts) {
  if (!ts) return null
  try {
    // Handle "12 May 2026, 08:30 UTC" format from our backend
    const date = new Date(ts)
    if (!isNaN(date.getTime())) {
      const now = new Date()
      const diffMs = now - date
      const diffH = Math.floor(diffMs / 3_600_000)
      const diffD = Math.floor(diffMs / 86_400_000)
      if (diffH < 1) return 'Just now'
      if (diffH < 24) return `${diffH}h ago`
      if (diffD < 7) return `${diffD}d ago`
      return date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })
    }
  } catch {
    // ignore
  }
  // Fallback: return raw (truncated)
  return ts.length > 20 ? ts.slice(0, 20) : ts
}

function ScoreBadge({ score }) {
  const color = score >= 60 ? 'text-green-400 bg-green-400/10 border-green-400/30'
    : score >= 40 ? 'text-yellow-400 bg-yellow-400/10 border-yellow-400/30'
    : 'text-red-400 bg-red-400/10 border-red-400/30'
  return (
    <div className={`inline-flex items-center justify-center w-12 h-12 rounded-full border-2 ${color} text-lg font-bold`}>
      {score}
    </div>
  )
}

function SentimentBar({ positive, negative, neutral, total }) {
  if (!total) return null
  const pPct = Math.round((positive / total) * 100)
  const nPct = Math.round((negative / total) * 100)
  const nuPct = 100 - pPct - nPct
  return (
    <div className="flex h-1.5 rounded-full overflow-hidden w-full mt-1">
      <div className="bg-green-400 transition-all" style={{ width: `${pPct}%` }} />
      <div className="bg-gray-600 transition-all" style={{ width: `${nuPct}%` }} />
      <div className="bg-red-400 transition-all" style={{ width: `${nPct}%` }} />
    </div>
  )
}

export default function NewsPanel({ data }) {
  if (!data) return null
  const {
    sentiment_score, overall_sentiment, articles_analyzed,
    positive_count, negative_count, neutral_count,
    top_news = [], key_themes = [], risk_alerts = [],
  } = data

  const sentimentColor = overall_sentiment === 'POSITIVE' ? 'text-green-400'
    : overall_sentiment === 'NEGATIVE' ? 'text-red-400' : 'text-gray-400'

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="card h-full flex flex-col"
    >
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-bold text-gray-200 uppercase tracking-wide">News & Sentiment</h3>
        <ScoreBadge score={sentiment_score} />
      </div>

      {/* Overall + counts */}
      <div className="mb-3">
        <div className="flex items-center gap-3 mb-1">
          <span className={`text-sm font-bold ${sentimentColor}`}>{overall_sentiment}</span>
          <div className="flex gap-2 text-xs">
            <span className="text-green-400 font-semibold">{positive_count}✓</span>
            <span className="text-red-400 font-semibold">{negative_count}✗</span>
            <span className="text-gray-500">{neutral_count}~</span>
          </div>
          <span className="text-gray-600 text-xs ml-auto">{articles_analyzed} articles</span>
        </div>
        <SentimentBar
          positive={positive_count}
          negative={negative_count}
          neutral={neutral_count}
          total={articles_analyzed}
        />
      </div>

      {/* Key Themes */}
      {key_themes.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {key_themes.map((t, i) => (
            <span key={i} className="badge text-xs bg-blue-400/10 text-blue-400 border border-blue-400/20">
              {t.replace(/_/g, ' ')}
            </span>
          ))}
        </div>
      )}

      {/* Risk Alerts */}
      {risk_alerts.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {risk_alerts.map((r, i) => (
            <span key={i} className="badge text-xs bg-red-400/10 text-red-400 border border-red-400/20">
              ⚠ {r}
            </span>
          ))}
        </div>
      )}

      {/* FinBERT model note */}
      <div className="flex items-center gap-1.5 mb-3">
        <div className="h-1.5 w-1.5 rounded-full bg-blue-400 animate-pulse" />
        <span className="text-gray-600 text-xs">Powered by FinBERT financial NLP</span>
      </div>

      {/* Articles */}
      <div className="space-y-2 flex-1 overflow-y-auto">
        {top_news.length === 0 ? (
          <div className="flex flex-col items-center py-4 text-gray-600">
            <Newspaper size={24} className="mb-2" />
            <p className="text-xs">No recent news found</p>
          </div>
        ) : (
          top_news.map((article, i) => {
            const ts = formatTimestamp(article.published_at)
            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                className="bg-gray-800 rounded-lg p-2.5 space-y-1.5"
              >
                <div className="flex items-start justify-between gap-2">
                  <p className="text-gray-200 text-xs font-medium leading-snug line-clamp-2 flex-1">
                    {article.headline}
                  </p>
                  {article.url && (
                    <a href={article.url} target="_blank" rel="noopener noreferrer"
                       className="text-gray-600 hover:text-gray-400 shrink-0 mt-0.5">
                      <ExternalLink size={10} />
                    </a>
                  )}
                </div>

                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-gray-500 text-xs font-medium">{article.source}</span>
                  {ts && (
                    <span className="text-gray-700 text-xs flex items-center gap-0.5">
                      <Clock size={9} />{ts}
                    </span>
                  )}
                  <SentimentBadge sentiment={article.sentiment} />
                  <ImpactBadge impact={article.impact} />
                </div>

                {article.reason && (
                  <p className="text-gray-600 text-xs italic leading-snug">{article.reason}</p>
                )}
              </motion.div>
            )
          })
        )}
      </div>
    </motion.div>
  )
}
