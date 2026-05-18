import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown } from 'lucide-react'

// Strip ALL markdown symbols from plain text
function stripMarkdown(text) {
  return text
    .replace(/\*\*(.+?)\*\*/g, '$1')   // **bold**
    .replace(/\*(.+?)\*/g, '$1')        // *italic*
    .replace(/`(.+?)`/g, '$1')          // `code`
    .replace(/^#{1,6}\s+/gm, '')        // # headers
    .replace(/^\s*[-*+]\s+/gm, '')      // bullet points
    .replace(/^\s*\d+\.\s+/gm, '')      // numbered lists
    .replace(/\|.+\|/g, '')             // markdown tables
    .replace(/^[-|=\s]+$/gm, '')        // table separators
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')  // [link](url) → link
    .replace(/_{1,2}(.+?)_{1,2}/g, '$1')      // _italic_
    .replace(/>\s*/g, '')               // blockquotes
    .replace(/\n{3,}/g, '\n\n')         // collapse extra blank lines
    .trim()
}

// Parse STOCKS_DATA blocks from the message
function parseContent(text) {
  const stocksRegex = /STOCKS_DATA::(\[[\s\S]*?\])::END_STOCKS_DATA/g
  const parts = []
  let lastIndex = 0
  let match

  while ((match = stocksRegex.exec(text)) !== null) {
    // Text before the block
    const before = text.slice(lastIndex, match.index).trim()
    if (before) parts.push({ type: 'text', content: stripMarkdown(before) })

    // The stocks block
    try {
      const stocks = JSON.parse(match[1])
      parts.push({ type: 'stocks', content: stocks })
    } catch {
      // Malformed JSON — show as plain text
      parts.push({ type: 'text', content: match[1] })
    }

    lastIndex = match.index + match[0].length
  }

  // Remaining text after last block
  const after = text.slice(lastIndex).trim()
  if (after) parts.push({ type: 'text', content: stripMarkdown(after) })

  if (parts.length === 0) parts.push({ type: 'text', content: stripMarkdown(text) })
  return parts
}

function StockCard({ stock, index }) {
  const isPositive = stock.change_percent >= 0
  const ticker = stock.ticker || ''
  const initial = ticker.charAt(0)

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="flex-shrink-0 w-40 bg-gray-900 border border-gray-700 rounded-xl p-3 space-y-2"
    >
      {/* Icon area */}
      <div className="w-10 h-10 rounded-lg bg-gray-800 border border-gray-700 flex items-center justify-center text-sm font-bold text-gray-300">
        {initial}
      </div>

      {/* Company name */}
      <div>
        <p className="text-white text-xs font-semibold leading-snug line-clamp-2">
          {stock.company || stock.ticker}
        </p>
        <p className="text-gray-500 text-xs">{ticker}</p>
      </div>

      {/* Price */}
      <div>
        <p className="text-white text-sm font-bold">
          ₹{stock.price?.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
        </p>
        <p className={`text-xs font-semibold flex items-center gap-0.5 ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
          {isPositive ? <TrendingUp size={10} /> : <TrendingDown size={10} />}
          {isPositive ? '+' : ''}{stock.change?.toFixed(2)} ({isPositive ? '+' : ''}{stock.change_percent?.toFixed(2)}%)
        </p>
      </div>
    </motion.div>
  )
}

function StocksGrid({ stocks }) {
  return (
    <div className="flex gap-3 overflow-x-auto pb-1 -mx-1 px-1">
      {stocks.map((stock, i) => (
        <StockCard key={stock.ticker || i} stock={stock} index={i} />
      ))}
    </div>
  )
}

function TextBlock({ content }) {
  // Split into paragraphs and render each
  const paragraphs = content.split(/\n\n+/).filter(p => p.trim())
  if (paragraphs.length === 0) return null
  return (
    <div className="space-y-2">
      {paragraphs.map((para, i) => (
        <p key={i} className="text-sm leading-relaxed">
          {para.split('\n').map((line, j) => (
            <span key={j}>
              {line}
              {j < para.split('\n').length - 1 && <br />}
            </span>
          ))}
        </p>
      ))}
    </div>
  )
}

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'

  if (isUser) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex justify-end mb-3"
      >
        <div className="max-w-[80%] bg-indigo-600 text-white rounded-2xl rounded-tr-sm px-4 py-2.5 text-sm leading-relaxed">
          {message.content}
        </div>
        <div className="w-7 h-7 rounded-full bg-gray-700 flex items-center justify-center text-xs font-bold text-gray-300 ml-2 mt-1 shrink-0">
          U
        </div>
      </motion.div>
    )
  }

  const parts = parseContent(message.content)

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex justify-start mb-3"
    >
      <div className="w-7 h-7 rounded-full bg-india-orange flex items-center justify-center text-xs font-bold text-white mr-2 mt-1 shrink-0">
        A
      </div>
      <div className="max-w-[90%] space-y-3">
        {parts.map((part, i) => (
          part.type === 'stocks'
            ? <StocksGrid key={i} stocks={part.content} />
            : (
              <div key={i} className="bg-gray-800 border border-gray-700 rounded-2xl rounded-tl-sm px-4 py-3 text-gray-200">
                <TextBlock content={part.content} />
              </div>
            )
        ))}
      </div>
    </motion.div>
  )
}
