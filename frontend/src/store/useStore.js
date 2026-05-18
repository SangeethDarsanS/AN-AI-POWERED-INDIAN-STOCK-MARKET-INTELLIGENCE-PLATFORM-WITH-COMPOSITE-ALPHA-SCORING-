import { create } from 'zustand'

const useStore = create((set) => ({
  currentTicker: '',
  currentExchange: 'NSE',
  analysisResult: null,
  isAnalyzing: false,
  error: null,
  chatSessionId: null,
  watchlist: [],

  setCurrentTicker: (ticker) => set({ currentTicker: ticker }),
  setCurrentExchange: (exchange) => set({ currentExchange: exchange }),
  setAnalysisResult: (result) => set({ analysisResult: result }),
  setIsAnalyzing: (val) => set({ isAnalyzing: val }),
  setError: (error) => set({ error }),
  setChatSessionId: (id) => set({ chatSessionId: id }),

  addToWatchlist: (ticker) =>
    set((state) => ({
      watchlist: state.watchlist.includes(ticker)
        ? state.watchlist
        : [...state.watchlist, ticker],
    })),

  removeFromWatchlist: (ticker) =>
    set((state) => ({
      watchlist: state.watchlist.filter((t) => t !== ticker),
    })),
}))

export default useStore
