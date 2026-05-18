import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Trash2, Bot } from 'lucide-react'
import MessageBubble from './MessageBubble'
import QuickActions from './QuickActions'
import { sendMessage, clearHistory } from '../../services/chatService'
import useStore from '../../store/useStore'

const WELCOME = {
  role: 'assistant',
  content: 'Namaste! I am Artha, your Indian market assistant.\n\nAsk me anything about NSE/BSE stocks. Top gainers, market overview, stock analysis, sector trends and more.',
}

export default function ChatInterface({ embedded = false }) {
  const [messages, setMessages] = useState([WELCOME])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  const { chatSessionId, setChatSessionId } = useStore()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => { scrollToBottom() }, [messages])

  const handleSend = async (text = input) => {
    const msg = text.trim()
    if (!msg || isLoading) return
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: msg }])
    setIsLoading(true)

    try {
      const res = await sendMessage(msg, chatSessionId)
      if (!chatSessionId) setChatSessionId(res.session_id)
      setMessages(prev => [...prev, { role: 'assistant', content: res.response }])
    } catch (e) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Sorry, I encountered an error: ${e.message}. Please try again.`,
      }])
    } finally {
      setIsLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleClear = async () => {
    if (chatSessionId) {
      await clearHistory(chatSessionId).catch(() => {})
      setChatSessionId(null)
    }
    setMessages([WELCOME])
  }

  return (
    <div className="flex flex-col h-full bg-gray-900 overflow-hidden" style={embedded ? {} : { borderRadius: '0.75rem', border: '1px solid rgb(31,41,55)' }}>
      {/* Header — hidden in embedded mode (FloatingChatButton has its own) */}
      {!embedded && (
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800 bg-gray-900">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-india-orange flex items-center justify-center">
              <Bot size={16} className="text-white" />
            </div>
            <div>
              <p className="text-sm font-bold text-white">Artha</p>
              <p className="text-xs text-gray-500">Indian Market AI Assistant</p>
            </div>
            <motion.div
              className="w-2 h-2 rounded-full bg-green-500 ml-1"
              animate={{ scale: [1, 1.3, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
          </div>
          <button
            onClick={handleClear}
            className="text-gray-600 hover:text-gray-400 transition-colors p-1.5 rounded-lg hover:bg-gray-800"
          >
            <Trash2 size={14} />
          </button>
        </div>
      )}

      {/* Quick Actions + clear button for embedded mode */}
      <div className="px-3 py-2 border-b border-gray-800 bg-gray-950 flex items-center gap-2">
        <div className="flex-1">
          <QuickActions onAction={handleSend} />
        </div>
        {embedded && (
          <button
            onClick={handleClear}
            className="shrink-0 text-gray-600 hover:text-gray-400 transition-colors p-1.5 rounded-lg hover:bg-gray-800"
            title="Clear chat"
          >
            <Trash2 size={13} />
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        <AnimatePresence>
          {messages.map((msg, i) => (
            <MessageBubble key={i} message={msg} isFirst={i === 0} />
          ))}
        </AnimatePresence>

        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex justify-start mb-3"
          >
            <div className="w-7 h-7 rounded-full bg-india-orange flex items-center justify-center text-xs font-bold text-white mr-2 mt-1">
              A
            </div>
            <div className="bg-gray-800 border border-gray-700 rounded-2xl rounded-tl-sm px-4 py-3">
              <div className="flex gap-1">
                {[0, 0.2, 0.4].map((delay, i) => (
                  <motion.div
                    key={i}
                    className="w-2 h-2 bg-gray-500 rounded-full"
                    animate={{ y: [0, -5, 0] }}
                    transition={{ duration: 0.8, repeat: Infinity, delay }}
                  />
                ))}
              </div>
            </div>
          </motion.div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-800 p-3">
        <div className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
            placeholder="Ask about any NSE/BSE stock..."
            disabled={isLoading}
            className="flex-1 bg-gray-800 border border-gray-700 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-india-orange transition-colors disabled:opacity-50"
          />
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => handleSend()}
            disabled={!input.trim() || isLoading}
            className="bg-india-orange hover:bg-orange-600 disabled:opacity-40 disabled:cursor-not-allowed text-white rounded-xl px-3.5 py-2.5 transition-colors"
          >
            <Send size={16} />
          </motion.button>
        </div>
        <p className="text-gray-700 text-xs mt-2 text-center">
          Not SEBI-registered advice. Do your own research before investing.
        </p>
      </div>
    </div>
  )
}
