import api from './api'

export const analyzeStock = (ticker, exchange = 'NSE') =>
  api.post('/analysis/full', { ticker: ticker.toUpperCase(), exchange }).then(r => r.data)

export const getFundamental = (ticker, exchange = 'NSE') =>
  api.post('/analysis/fundamental', { ticker: ticker.toUpperCase(), exchange }).then(r => r.data)

export const getTechnical = (ticker, exchange = 'NSE') =>
  api.post('/analysis/technical', { ticker: ticker.toUpperCase(), exchange }).then(r => r.data)

export const getSentiment = (ticker, exchange = 'NSE') =>
  api.post('/analysis/sentiment', { ticker: ticker.toUpperCase(), exchange }).then(r => r.data)

export const getCachedAnalysis = (ticker) =>
  api.get(`/analysis/cached/${ticker.toUpperCase()}`).then(r => r.data)

export const getMarketIndices = () =>
  api.get('/market/indices').then(r => r.data)

export const getTopGainers = (exchange = 'NSE', limit = 10) =>
  api.get(`/market/gainers?exchange=${exchange}&limit=${limit}`).then(r => r.data)

export const getTopLosers = (exchange = 'NSE', limit = 10) =>
  api.get(`/market/losers?exchange=${exchange}&limit=${limit}`).then(r => r.data)

export const getDhandhoScore = (ticker, exchange = 'NSE') =>
  api.get(`/dhandho/score/${ticker.toUpperCase()}?exchange=${exchange}`).then(r => r.data)

export const getSMD = (ticker) =>
  api.get(`/analysis/smd/${ticker.toUpperCase()}`).then(r => r.data)

export const getStrategyStocks = (strategyId) =>
  api.get(`/market/screener/${strategyId}`).then(r => r.data)
