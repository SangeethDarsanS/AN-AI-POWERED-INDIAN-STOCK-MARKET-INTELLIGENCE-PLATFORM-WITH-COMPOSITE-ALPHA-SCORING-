import api from './api'

export const sendMessage = (message, sessionId = null) =>
  api.post('/chat/message', { message, session_id: sessionId }).then(r => r.data)

export const getHistory = (sessionId) =>
  api.get(`/chat/history/${sessionId}`).then(r => r.data)

export const clearHistory = (sessionId) =>
  api.delete(`/chat/history/${sessionId}`).then(r => r.data)
