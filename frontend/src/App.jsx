import MarketOverview from './components/Dashboard/MarketOverview'
import AnalysisWindow from './components/AnalysisWindow'
import StrategyPanel from './components/StrategyPanel/StrategyPanel'
import FloatingChatButton from './components/ChatbotWindow/FloatingChatButton'

export default function App() {
  return (
    <div className="min-h-screen bg-gray-950 flex flex-col">
      {/* Top Header */}
      <header className="bg-gray-900 border-b border-gray-800 px-4 py-3 z-30 relative">
        <div className="max-w-screen-2xl mx-auto flex items-center">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🇮🇳</span>
            <div>
              <h1 className="text-lg font-black text-white tracking-tight leading-none">
                <span className="text-india-orange">Stocks</span> AI
              </h1>
              <p className="text-gray-500 text-xs leading-none">Indian Market Intelligence</p>
            </div>
          </div>
        </div>
      </header>

      {/* Market Overview Bar */}
      <MarketOverview />

      {/* Main Layout: Strategy Sidebar + Analysis */}
      <div className="flex flex-1 overflow-hidden">
        {/* Strategy Sidebar */}
        <StrategyPanel />

        {/* Analysis Area */}
        <main className="flex-1 overflow-y-auto p-4" style={{ minHeight: 'calc(100vh - 140px)' }}>
          <div className="max-w-screen-xl mx-auto">
            <AnalysisWindow />
          </div>
        </main>
      </div>

      {/* Floating Chatbot (Artha) */}
      <FloatingChatButton />
    </div>
  )
}
