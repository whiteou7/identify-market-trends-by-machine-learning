import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export function fetchElbow(params = {}) {
  return api.get('/elbow', { params }).then(r => r.data)
}

export function fetchAnalysis(params = {}) {
  return api.get('/analysis', { params }).then(r => r.data)
}

export function fetchUploadInfo() {
  return api.get('/upload/info').then(r => r.data)
}

export function uploadDataset(file) {
  const form = new FormData()
  form.append('file', file)
  return api.post('/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then(r => r.data)
}

export function clearUpload() {
  return api.delete('/upload').then(r => r.data)
}
