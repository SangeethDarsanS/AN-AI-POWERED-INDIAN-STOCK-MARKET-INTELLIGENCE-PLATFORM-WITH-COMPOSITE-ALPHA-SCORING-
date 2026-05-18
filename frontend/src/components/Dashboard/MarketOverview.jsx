import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, Activity } from 'lucide-react'
import { getMarketIndices } from '../../services/stockService'

function IndexCard({ name, value, change, change_percent }) {
  const isPositive = change_percent >= 0
  return (
    <motion.div
      className="flex items-center gap-3 px-4 py-2 bg-gray-900 rounded-lg border border-gray-800"
      whileHover={{ scale: 1.02 }}
    >
      <div>
        <p className="text-gray-400 text-xs font-medium">{name}</p>
        <p className="text-white font-bold text-sm">
          {value > 0 ? value.toLocaleString('en-IN', { maximumFractionDigits: 2 }) : '--'}
        </p>
      </div>
      <div className={`flex items-center gap-1 text-xs font-semibold ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
        {isPositive ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
        <span>{change_percent > 0 ? '+' : ''}{change_percent?.toFixed(2)}%</span>
      </div>
    </motion.div>
  )
}

export default function MarketOverview() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['market-indices'],
    queryFn: getMarketIndices,
    refetchInterval: 60000,
  })

  return (
    <div className="bg-gray-950 border-b border-gray-800 px-4 py-2">
      <div className="max-w-screen-2xl mx-auto flex items-center gap-2 overflow-x-auto">
        <div className="flex items-center gap-1.5 text-gray-500 mr-3 shrink-0">
          <Activity size={14} />
          <span className="text-xs font-medium">LIVE</span>
          <motion.div
            className="w-1.5 h-1.5 rounded-full bg-green-500"
            animate={{ opacity: [1, 0, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
        </div>
        {isLoading && (
          <div className="text-gray-500 text-xs">Loading market data...</div>
        )}
        {isError && (
          <div className="text-gray-600 text-xs">Market data unavailable</div>
        )}
        {data && (
          <>
            <IndexCard {...(data.nifty50 || {})} />
            <IndexCard {...(data.sensex || {})} />
            <IndexCard {...(data.bank_nifty || {})} />
            <IndexCard {...(data.india_vix || {})} />
          </>
        )}
      </div>
    </div>
  )
}
