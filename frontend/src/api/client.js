import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 60000,
})

export const analyseEmail = (payload)        => api.post('/api/analyse', payload)
export const rewriteEmail = (payload)        => api.post('/api/rewrite', payload)
export const analyseThread = (payload)       => api.post('/api/analyse-thread', payload)
export const getSenderProfile = (name)       => api.get(`/api/sender/${encodeURIComponent(name)}`)
export const listSenders = ()                => api.get('/api/senders')

export default api
