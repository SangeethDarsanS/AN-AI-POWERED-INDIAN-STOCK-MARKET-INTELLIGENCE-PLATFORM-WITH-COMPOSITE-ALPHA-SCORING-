import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, MessageCircle, Minus } from 'lucide-react'
import ChatInterface from './ChatInterface'

export default function FloatingChatButton() {
  const [open, setOpen] = useState(false)
  const [minimized, setMinimized] = useState(false)

  return (
    <>
      {/* Floating Button — always visible when chat is closed */}
      <AnimatePresence>
        {!open && (
          <motion.button
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => { setOpen(true); setMinimized(false) }}
            className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full shadow-2xl flex items-center justify-center overflow-hidden border-2 border-india-orange/60"
            style={{ background: 'linear-gradient(135deg, #FF6B00, #e85500)' }}
            title="Chat with Artha"
          >
            {/* Avatar face */}
            <div className="flex flex-col items-center justify-center leading-none select-none">
              <span className="text-xl leading-none">🤖</span>
            </div>

            {/* Pulse ring */}
            <span className="absolute w-full h-full rounded-full animate-ping bg-india-orange/30 pointer-events-none" />
          </motion.button>
        )}
      </AnimatePresence>

      {/* Chat Window */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, scale: 0.85, y: 20, originX: 1, originY: 1 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.85, y: 20 }}
            transition={{ duration: 0.2, ease: 'easeOut' }}
            className="fixed bottom-6 right-6 z-50 shadow-2xl rounded-2xl overflow-hidden border border-gray-700"
            style={{ width: 380, height: minimized ? 52 : 580 }}
          >
            {/* Custom header with controls */}
            <div
              className="flex items-center justify-between px-4 py-3 bg-gray-900 border-b border-gray-800 cursor-pointer select-none"
              onClick={() => setMinimized(!minimized)}
            >
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-india-orange flex items-center justify-center text-base shadow-md">
                  🤖
                </div>
                <div>
                  <p className="text-sm font-bold text-white leading-none">Artha</p>
                  <p className="text-xs text-gray-500 leading-none mt-0.5">Indian Market AI</p>
                </div>
                <motion.div
                  className="w-2 h-2 rounded-full bg-green-400 ml-1"
                  animate={{ scale: [1, 1.4, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
              </div>
              <div className="flex items-center gap-1">
                <button
                  onClick={(e) => { e.stopPropagation(); setMinimized(!minimized) }}
                  className="text-gray-500 hover:text-gray-300 p-1.5 rounded-lg hover:bg-gray-800 transition-colors"
                >
                  <Minus size={13} />
                </button>
                <button
                  onClick={(e) => { e.stopPropagation(); setOpen(false) }}
                  className="text-gray-500 hover:text-red-400 p-1.5 rounded-lg hover:bg-gray-800 transition-colors"
                >
                  <X size={13} />
                </button>
              </div>
            </div>

            {/* Chat body — hidden when minimized */}
            {!minimized && (
              <div className="h-full" style={{ height: 'calc(580px - 52px)' }}>
                <ChatInterface embedded />
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
